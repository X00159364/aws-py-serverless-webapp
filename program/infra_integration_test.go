package test

import (
	// "fmt"
	// "io/ioutil"
	// "net/http"
	"os"
	// "strings"
	"testing"
	// "time"

	"github.com/pulumi/pulumi/pkg/v2/testing/integration"
	// "github.com/pulumi/pulumi/pkg/testing/integration"
	// "github.com/stretchr/testify/assert"
	// "github.com/aws/aws-sdk-go/aws/credentials"
	// "github.com/aws/aws-sdk-go/aws/signer/v4"
)

func TestDeployResources(t *testing.T) {
	awsRegion := os.Getenv("AWS_REGION")
	if awsRegion == "" {
		awsRegion = "eu-west-1"
	}
	cwd, _ := os.Getwd()
	integration.ProgramTest(t, &integration.ProgramTestOptions{
		Quick:       true,
		SkipRefresh: true,
		Dir:         cwd,
		Config: map[string]string{
			"aws:region": awsRegion,
		},
	})
}