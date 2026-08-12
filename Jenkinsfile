#!groovy

retry (10) {
    // load pipeline configuration into the environment
    httpRequest("${FEDORA_CI_PIPELINES_CONFIG_URL}/environment").content.split('\n').each { l ->
        l = l.trim(); if (l && !l.startsWith('#')) { env["${l.split('=')[0].trim()}"] = "${l.split('=')[1].trim()}" }
    }
}

def pipelineMetadata = [
    pipelineName: 'rpmdeplint',
    pipelineDescription: 'Finding errors in RPM packages in the context of their dependency graph',
    testCategory: 'functional',
    testType: 'rpmdeplint',
    maintainer: 'Fedora CI',
    docs: 'https://docs.fedoraproject.org/en-US/ci/generic_tests/#_rpmdeplint',
    contact: [
        irc: '#fedora-ci',
        email: 'ci@lists.fedoraproject.org'
    ],
]
def testingFarmRequestId
def testingFarmResult
def pipelineRepoUrlAndRef
def hook
def runUrl


pipeline {

    agent none

    libraries {
        lib("fedora-pipeline-library@${env.PIPELINE_LIBRARY_VERSION}")
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: env.DEFAULT_DAYS_TO_KEEP_LOGS, artifactNumToKeepStr: env.DEFAULT_ARTIFACTS_TO_KEEP))
        timeout(time: env.DEFAULT_PIPELINE_TIMEOUT_MINUTES, unit: 'MINUTES')
        skipDefaultCheckout(true)
    }

    parameters {
        string(name: 'BODHI_UPDATE_ID', defaultValue: '', trim: true, description: 'Bodhi updated ID; Example: FEDORA-2025-7826f19244')
        string(name: 'ARTIFACT_IDS', defaultValue: '', trim: true, description: 'A comma-separated list of all koji builds in the update; Example: koji-build:46436038')
        string(name: 'DIST_GIT_BRANCH', defaultValue: '', trim: true, description: 'Dist-git branch associated with the provided BODHI_UPDATE_ID')
        booleanParam(name: 'MULTIHOST_PIPELINE', defaultValue: false, description: 'Use the new testing-farm multihost-pipeline')
    }

    environment {
        TESTING_FARM_API_KEY = credentials('testing-farm-api-key')
    }

    stages {
        stage('Prepare') {
            agent {
                label pipelineMetadata.pipelineName
            }
            steps {
                script {
                    if (!params.BODHI_UPDATE_ID) {
                        abort('BODHI_UPDATE_ID is missing')
                    }
                    if (!params.ARTIFACT_IDS) {
                        abort('ARTIFACT_IDS is missing')
                    }
                    if (!params.DIST_GIT_BRANCH) {
                        abort('DIST_GIT_BRANCH is missing')
                    }
                    currentBuild.displayName = params.BODHI_UPDATE_ID
                    checkout scm
                    pipelineRepoUrlAndRef = [url: "${getGitUrl()}", ref: "${getGitRef()}"]
                }
                sendMessage(type: 'queued', additionalArtifactIds: params.ARTIFACT_IDS, pipelineMetadata: pipelineMetadata, dryRun: isPullRequest())
            }
        }

        stage('Schedule Test') {
            agent {
                label pipelineMetadata.pipelineName
            }
            steps {
                script {
                    def requestPayload = [
                        api_key: "${env.TESTING_FARM_API_KEY}",
                        test: [
                            fmf: pipelineRepoUrlAndRef
                        ],
                        environments: [
                            [
                                arch: "x86_64",
                                variables: [
                                    BODHI_UPDATE_ID: params.BODHI_UPDATE_ID,
                                ],
                                tmt: [
                                    context: [
                                        "dist-git-branch": params.DIST_GIT_BRANCH,
                                    ]
                                ]
                            ]
                        ]
                    ]
                    if (params.MULTIHOST_PIPELINE) {
                        requestPayload['settings'] = [
                            pipeline: [
                                type: "tmt-multihost"
                            ]
                        ]
                        requestPayload['environments'][0]["tmt"]["policy"] = "fedora-ci"
                    }

                    hook = registerWebhook()
                    requestPayload['notification'] = ['webhook': [url: hook.getURL()]]

                    def response = submitTestingFarmRequest(payloadMap: requestPayload)
                    testingFarmRequestId = response['id']
                    runUrl = "${FEDORA_CI_TESTING_FARM_ARTIFACTS_URL}/${testingFarmRequestId}"
                }
                sendMessage(type: 'running', additionalArtifactIds: params.ARTIFACT_IDS, pipelineMetadata: pipelineMetadata, runUrl: runUrl, dryRun: isPullRequest())
            }
        }

        stage('Wait for Test Results') {
            agent none
            steps {
                script {
                    def response = waitForTestingFarm(requestId: testingFarmRequestId, hook: hook)
                    testingFarmResult = response.apiResponse
                }
            }
        }
    }

    post {
        always {
            evaluateTestingFarmResults(testingFarmResult)
        }
        aborted {
            script {
                if (isTimeoutAborted(timeout: env.DEFAULT_PIPELINE_TIMEOUT_MINUTES, unit: 'MINUTES')) {
                    sendMessage(type: 'error', additionalArtifactIds: params.ARTIFACT_IDS, errorReason: 'Timeout has been exceeded, pipeline aborted.', pipelineMetadata: pipelineMetadata, runUrl: runUrl, dryRun: isPullRequest())
                }
            }
        }
        success {
            sendMessage(type: 'complete',  additionalArtifactIds: params.ARTIFACT_IDS, pipelineMetadata: pipelineMetadata, runUrl: runUrl, dryRun: isPullRequest())
        }
        failure {
            sendMessage(type: 'error', additionalArtifactIds: params.ARTIFACT_IDS, pipelineMetadata: pipelineMetadata, runUrl: runUrl, dryRun: isPullRequest())
        }
        unstable {
            sendMessage(type: 'complete', additionalArtifactIds: params.ARTIFACT_IDS, pipelineMetadata: pipelineMetadata, runUrl: runUrl, dryRun: isPullRequest())
        }
    }
}
