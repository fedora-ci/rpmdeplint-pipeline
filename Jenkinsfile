#!groovy

@Library('fedora-pipeline-library@prototype') _

def pipelineMetadata = [
    pipelineName: 'rpmdeplint',
    pipelineDescription: 'Finding errors in RPM packages in the context of their dependency graph',
    testCategory: 'functional',
    testType: 'rpmdeplint',
    maintainer: 'Fedora CI',
    docs: 'https://github.com/fedora-ci/rpmdeplint-pipeline',
    contact: [
        irc: '#fedora-ci',
        email: 'ci@lists.fedoraproject.org'
    ],
]
def artifactId
def testingFarmResult


pipeline {

    options {
        buildDiscarder(logRotator(daysToKeepStr: '180', artifactNumToKeepStr: '100'))
        throttle(['max-10'])
        timeout(time: 4, unit: 'HOURS')
    }

    agent {
        label 'master'
    }

    parameters {
        string(name: 'ARTIFACT_ID', defaultValue: '', trim: true, description: '"koji-build:&lt;taskId&gt;" for Koji builds; Example: koji-build:46436038')
        string(name: 'ADDITIONAL_ARTIFACT_IDS', defaultValue: '', trim: true, description: 'A comma-separated list of additional ARTIFACT_IDs')
    }

    environment {
        TESTING_FARM_API_KEY = credentials('testing-farm-api-key')
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    artifactId = params.ARTIFACT_ID

                    if (!artifactId) {
                        abort('ARTIFACT_ID is missing')
                    }
                }
                setBuildNameFromArtifactId(artifactId: artifactId)
                sendMessage(type: 'queued', artifactId: artifactId, pipelineMetadata: pipelineMetadata, dryRun: isPullRequest())
            }
        }

        stage('Test') {
            steps {
                sendMessage(type: 'running', artifactId: artifactId, pipelineMetadata: pipelineMetadata, dryRun: isPullRequest())

                script {
                    def requestPayload = """
                        {
                            "api_key": "${env.TESTING_FARM_API_KEY}",
                            "test": {
                                "fmf": {
                                    "url": "${getGitUrl()}",
                                    "ref": "${getGitRef()}"
                                }
                            },
                            "environments": [
                                {
                                    "arch": "x86_64",
                                    "variables": {
                                        "RELEASE_ID": "${getReleaseIdFromBranch()}",
                                        "TASK_ID": "${artifactId.split(':')[1]}"
                                    }
                                }
                            ]
                        }
                    """
                    // def response = submitTestingFarmRequest(payload: requestPayload)
                    // testingFarmResult = waitForTestingFarmResults(requestId: response['id'], timeout: 60)
                    // evaluateTestingFarmResults(testingFarmResult)
                    // testingFarmResult = ['result': ['xunit': '<testsuites overall-result=\"passed\"><properties/><testsuite overall-result=\"passed\" tests=\"1\"><properties><property name=\"baseosci.overall-result\" value=\"PASSED\"/></properties><testcase name=\"/rpmdeplint\" result=\"passed\"><properties><property name=\"baseosci.arch\" value=\"x86_64\"/><property name=\"baseosci.connectable_host\" value=\"localhost\"/><property name=\"baseosci.distro\" value=\"\"/><property name=\"baseosci.status\" value=\"Complete\"/><property name=\"baseosci.testcase.source.url\" value=\"\"/><property name=\"baseosci.variant\" value=\"\"/></properties><logs><log href=\"work-rpmdeplintmqD9s8/rpmdeplint/execute/rpmdeplint\" name=\"log_dir\"/><log href=\"work-rpmdeplintmqD9s8/rpmdeplint/execute/rpmdeplint/out.log\" name=\"testout.log\"/></logs><testing-environment name=\"requested\"><property name=\"arch\" value=\"x86_64\"/><property name=\"compose\" value=\"localhost\"/></testing-environment><testing-environment name=\"provisioned\"><property name=\"arch\" value=\"x86_64\"/><property name=\"compose\" value/></testing-environment></testcase></testsuite></testsuites>']]
                }
            }
        }
    }

    post {
        success {
            xunit(
                thresholds: [skipped(failureThreshold: '0'), failed(failureThreshold: '0')],
                tools: [JUnit(pattern: 'xunit.xml')]
            )
        }
    }
}
