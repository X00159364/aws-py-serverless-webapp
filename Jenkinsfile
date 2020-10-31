pipeline {
    agent any

    environment {
        BUILD_URL = "${BUILD_URL}"
    }

    stages {
    
        stage ("Pulumi up") {
            steps {
                nodejs(nodeJSInstallationName: "Node") {
                    withEnv(["PATH+PULUMI=C:/ProgramData/chocolatey/lib/pulumi/tools/Pulumi/bin"]) {
                        bat "cd /program"
                        bat "dir"
                        bat "pulumi stack select ${PULUMI_STACK}"
                        bat "pulumi up --yes"
                    }
                }
            }
        }
        
        stage ("Pulumi Destroy") {
            steps {
                nodejs(nodeJSInstallationName: "Node") {
                    withEnv(["PATH+PULUMI=C:/ProgramData/chocolatey/lib/pulumi/tools/Pulumi/bin"]) {
                        sleep(60)
                        bat "pulumi stack select ${PULUMI_STACK}"
                        bat "pulumi destroy --yes"
                    }
                }
            }
        }
    }
    post {
        // failure{
        //     currentBuild.result = 'FAILURE'
        // }
        // success{
        //     currentBuild.result = 'SUCCESS'
        // }            
        always {
            influxDbPublisher(selectedTarget: 'JenkinsDB', customData: assignURL(BUILD_URL))
        }
    }    
}

def assignURL(build_url) {
    def buildURL = [:]
    buildURL['url'] = build_url
    return buildURL
}
