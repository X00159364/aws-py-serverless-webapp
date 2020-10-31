from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)
import json


# Check for DynamoDB stream enabled value
def dynamodb_stream_validation(args: ResourceValidationArgs, report_violation: ReportViolation):
    if args.resource_type == "aws:dynamodb/table:Table" and "streamEnabled" in args.props:
        stream_value = args.props["streamEnabled"]
        if stream_value != True:
            report_violation("For this program to work DynamoDB streams need to be enabled")

stream_check = ResourceValidationPolicy(
    name="dynamodb_stream_check",
    description="Check if streams are enabled.",
    validate=dynamodb_stream_validation,
)

# Check if policies are included
def iam_policy_validation(args: ResourceValidationArgs, report_violation: ReportViolation):
    if args.resource_type == "aws:iam/rolePolicy:RolePolicy" and "policy" in args.props:
        policy = json.loads(args.props["policy"])
        policies = policy["Statement"][0]["Action"]
        if "s3:PutObject" not in policies or "polly:SynthesizeSpeech" not in policies:
            report_violation("For this program to work S3 and Polly policies needed")

policy_check = ResourceValidationPolicy(
    name="s3-polly-policy",
    description="Check if permissions are present.",
    validate=iam_policy_validation,
)




PolicyPack(
    name="aws-python",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        stream_check
        # policy_check
    ],
)