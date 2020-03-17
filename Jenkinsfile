#!groovy

@Library('fedora-pipeline-library@prototype') _

def pipelineMetadata = [
    pipelineName: 'rpmdeplint',
    pipelineDescription: 'TODO',
    testCategory: 'integration',
    testType: 'tier1',
    maintainer: 'Fedora CI',
    docs: 'https://somewhere.com/user-documentation',
    contact: [
        irc: '#fedora-ci',
        email: 'fedora-ci@fedoraproject.org'
    ],
]
def artifactId
def dryRun = isPullRequest() ? true : false

pipeline {

    agent {
        label 'fedora-ci-agent'
    }

    parameters {
        string(name: 'ARTIFACT_ID', defaultValue: '', description: '"koji-build:<taskId>" for Koji builds; Example: koji-build:42376994')
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    artifactId = params.ARTIFACT_ID
                }
                sendMessage(type: 'running', artifactId: artifactId, pipelineMetadata: pipelineMetadata, dryRun: dryRun)
            }
        }

        stage('Test') {
            steps {
                script {
                    echo 'Call Testing Farm here and wait for results...'
                }
            }
        }

        stage('Archive Results') {
            steps {
                script {
                    echo 'Fetch results from Testing Farm and archive them (if needed).'
                }
            }
        }
    }

    post { 
        success { 
            echo 'Publish results and send email(s).'
        }
        failure { 
            echo 'Publish results and send email(s).'
        }
        unstable { 
            echo 'Publish results and send email(s).'
        }
    }
}
