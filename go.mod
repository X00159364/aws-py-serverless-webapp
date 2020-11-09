module github.com/X00159364/aws-py-serverless-webapp/m/v2

go 1.15

require (
	github.com/aws/aws-sdk-go v1.29.27
	github.com/aws/aws-sdk-go-v2 v0.29.0
	github.com/aws/aws-sdk-go-v2/service/dynamodb v0.29.0
	github.com/pkg/errors v0.9.1
	github.com/pulumi/pulumi-eks v0.20.0
	github.com/pulumi/pulumi/pkg v1.14.1
	github.com/pulumi/pulumi/pkg/v2 v2.0.0
	github.com/stretchr/testify v1.6.1
)

replace github.com/Azure/go-autorest => github.com/Azure/go-autorest v12.4.3+incompatible
