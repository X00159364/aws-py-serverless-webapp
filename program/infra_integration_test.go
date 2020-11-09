package test

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/pulumi/pulumi/pkg/v2/testing/integration"
	// "github.com/pulumi/pulumi/pkg/testing/integration"
	"github.com/stretchr/testify/assert"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/signer/v4"
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
		Dir: cwd,
		Config: map[string]string{
			"aws:region": awsRegion,
		},
		ExtraRuntimeValidation: func(t *testing.T, stack integration.RuntimeValidationStackInfo) {
			// maxWait := 10 * time.Minute
			// maxWait := 1 * time.Minute
			endpoint := stack.Outputs["serverless_api_url"].(string)
			// assertHTTPResultWithRetry(t, endpoint, nil, maxWait, func(body string) bool {
			// 	return assert.Contains(t, body, "Noel")			
			// })
			// Sample JSON document to be included as the request body
			json := `{ "firstName": "Noel", "lastName": "Lowry" }`
			body := strings.NewReader(json)
			print(body)
			// Get credentials from environment variables and create the AWS Signature Version 4 signer
			credentials := credentials.NewEnvCredentials()
			signer := v4.NewSigner(credentials)

			// An HTTP client for sending the request
			client := &http.Client{}

			// Form the HTTP request
			req, err := http.NewRequest(http.MethodPut, endpoint, body)
			if err != nil {
				fmt.Print(err)
			}

			// You can probably infer Content-Type programmatically, but here, we just say that it's JSON
			req.Header.Add("Content-Type", "application/json")

			// Sign the request, send it, and print the response
			signer.Sign(req, body, "apigateway", awsRegion, time.Now())
			resp, err := client.Do(req)
			if err != nil {
				fmt.Print(err)
			}
			fmt.Print(resp.Status + "\n")	
			assert.Contains(t, body, "Noel")			
		},		
	})
}


func assertHTTPResult(t *testing.T, output interface{}, headers map[string]string, check func(string) bool) bool {
	return assertHTTPResultWithRetry(t, output, headers, 5*time.Minute, check)
}

func assertHTTPResultWithRetry(t *testing.T, output interface{}, headers map[string]string, maxWait time.Duration, check func(string) bool) bool {
	return assertHTTPResultShapeWithRetry(t, output, headers, maxWait, func(string) bool { return true }, check)
}

// assertHTTPResultWithRetry(					t, 		endpoint, 				nil, 				maxWait, func(body string) bool {
func assertHTTPResultShapeWithRetry(t *testing.T, output interface{}, headers map[string]string, maxWait time.Duration,
	ready func(string) bool, check func(string) bool) bool {
	hostname, ok := output.(string)
	print(hostname)
	if !assert.True(t, ok, fmt.Sprintf("expected `%s` output", output)) {
		return false
	}

	hostname = hostname
	// if !(strings.HasPrefix(hostname, "http://") || strings.HasPrefix(hostname, "https://")) {
	// 	hostname = fmt.Sprintf("http://%s", hostname)
	// }

	startTime := time.Now()
	count, sleep := 0, 0
	for {
		now := time.Now()
		req, err := http.NewRequest("POST", hostname, nil)
		if !assert.NoError(t, err) {
			return false
		}

		for k, v := range headers {
			// Host header cannot be set via req.Header.Set(), and must be set
			// directly.
			if strings.ToLower(k) == "host" {
				req.Host = v
				continue
			}
			req.Header.Set(k, v)
		}

		client := &http.Client{Timeout: time.Second * 10}
		resp, err := client.Do(req)
		if err == nil && resp.StatusCode == 200 {
			if !assert.NotNil(t, resp.Body, "resp.body was nil") {
				return false
			}

			// Read the body
			defer resp.Body.Close()
			body, err := ioutil.ReadAll(resp.Body)
			if !assert.NoError(t, err) {
				return false
			}

			bodyText := string(body)

			// Even if we got 200 and a response, it may not be ready for assertion yet - that's specific per test.
			if ready(bodyText) {
				// Verify it matches expectations
				return check(bodyText)
			}
		}
		if now.Sub(startTime) >= maxWait {
			fmt.Printf("Timeout after %v. Unable to http.get %v successfully.", maxWait, hostname)
			return false
		}
		count++
		// delay 10s, 20s, then 30s and stay at 30s
		if sleep > 30 {
			sleep = 30
		} else {
			sleep += 10
		}
		time.Sleep(time.Duration(sleep) * time.Second)
		fmt.Printf("Http Error: %v\n", err)
		fmt.Printf("  Retry: %v, elapsed wait: %v, max wait %v\n", count, now.Sub(startTime), maxWait)
	}

	return false
}
