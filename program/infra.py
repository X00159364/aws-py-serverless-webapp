import os
import mimetypes
import json
import pulumi
from pulumi import AssetArchive, export, FileArchive, FileAsset, ResourceOptions
from pulumi_aws import apigateway, cloudwatch, sns, dynamodb, ec2, ecr, ecs, iam, kinesis, lambda_, sqs, s3

lambda_role = iam.Role('lambdaRole',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }"""
)

lambda_role_policy = iam.RolePolicy('lambdaRolePolicy',
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }]
    }"""
)

lambda_fn = lambda_.Function('lambda_function',
   role=lambda_role.arn,
   runtime="python3.8",
   handler="lambda.lambda_handler",
   timeout=10,
   code=AssetArchive({
       '.': FileArchive('./lambda')
   })
) 

dynamo_role_policy = iam.RolePolicy('dynamoRolePolicy',
    role=lambda_role.id,
    policy="""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:eu-west-1:592715633892:*"

        }
        ]
    }"""
)

serverless_webapp_api = apigateway.RestApi("serverless_webapp_API", 
    description="API for serverless web application",
        endpoint_configuration = {
        "types" : "REGIONAL"
    })

serverless_webapp_method = apigateway.Method("serverless_webapp_Method",
    authorization="NONE",
    http_method="POST",
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api.id)

serverless_webapp_options_method = apigateway.Method("serverless_webapp_options_Method",
    authorization="NONE",
    http_method="OPTIONS",
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api.id)

serverless_webapp_integration = apigateway.Integration("serverless_webapp_Integration",
    http_method=serverless_webapp_method.http_method,
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api,
    integration_http_method='POST',
    type="AWS",                
    uri=lambda_fn.invoke_arn)

serverless_webapp_options_integration = apigateway.Integration("serverless_webapp_options_Integration",
    http_method=serverless_webapp_options_method.http_method,
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api,    
    type="MOCK",
    __opts__=ResourceOptions(depends_on=[serverless_webapp_options_method]))

response200 = apigateway.MethodResponse("response200",    
    http_method=serverless_webapp_method.http_method,
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api.id,
    response_models = {
        "application/json": "Empty"
    },    
    status_code="200",
    response_parameters={
        "method.response.header.Access-Control-Allow-Headers": True,
        "method.response.header.Access-Control-Allow-Methods": True,
        "method.response.header.Access-Control-Allow-Origin": True
    },
    ) 

options_response200 = apigateway.MethodResponse("options_response200",    
    http_method=serverless_webapp_options_method.http_method,
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api.id,
    response_models = {
        "application/json": "Empty"
    },    
    status_code="200",
    response_parameters={
        "method.response.header.Access-Control-Allow-Headers": True,
        "method.response.header.Access-Control-Allow-Methods": True,
        "method.response.header.Access-Control-Allow-Origin": True
    },
    )     

serverless_webapp_integration_response = apigateway.IntegrationResponse("serverless_webapp_IntegrationResponse",
    http_method=serverless_webapp_method.http_method,
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api.id,
    status_code=response200.status_code,
    __opts__=ResourceOptions(depends_on=[lambda_fn]))

serverless_webapp_options_integration_response = apigateway.IntegrationResponse("serverless_webapp_options_IntegrationResponse",
    http_method=serverless_webapp_options_method.http_method,
    resource_id=serverless_webapp_api.root_resource_id,
    rest_api=serverless_webapp_api.id,
    status_code=options_response200.status_code,
    # status_code="200",
    __opts__=ResourceOptions(depends_on=[lambda_fn]))

serverless_dep = apigateway.Deployment(
    'example',
    rest_api=serverless_webapp_api,
    stage_name="dev",
    __opts__=ResourceOptions(depends_on=[serverless_webapp_integration])
)

lambda_permission = lambda_.Permission(
    "lambdaPermission",
    action="lambda:InvokeFunction",
    function=lambda_fn.name,
    principal="apigateway.amazonaws.com",
    source_arn=serverless_webapp_api.execution_arn.apply(
        lambda execution_arn: f"{execution_arn}/*/*/*"
    ),
    opts=ResourceOptions(depends_on=[lambda_fn, serverless_dep]),
)

dynamodb_table = dynamodb.Table("serverless-webapp-db",
    attributes=[
        dynamodb.TableAttributeArgs(
            name="ID",
            type="S",
        ),
        dynamodb.TableAttributeArgs(
            name="LatestGreetingTime",
            type="S",
        ),
    ],
    billing_mode="PROVISIONED",
    hash_key="ID",
    range_key="LatestGreetingTime",
    read_capacity=20,
    write_capacity=20)

web_bucket = s3.Bucket('serverless-app-bucket', 
    website={
        "index_document": "index.html"
    }
)

content_dir = "www"
for file in os.listdir(content_dir):
    filepath = os.path.join(content_dir, file)
    mime_type, _ = mimetypes.guess_type(filepath)
    obj = s3.BucketObject(file,
        bucket=web_bucket.id,
        source=FileAsset(filepath), 
        content_type=mime_type)

def public_read_policy_for_bucket(serverless_webapp_bucket_name):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{serverless_webapp_bucket_name}/*",
            ]
        }]
    })

serverless_webapp_bucket_name = web_bucket.id

bucket_policy = s3.BucketPolicy("bucket-policy",
    bucket=serverless_webapp_bucket_name,
    policy=serverless_webapp_bucket_name.apply(public_read_policy_for_bucket))
