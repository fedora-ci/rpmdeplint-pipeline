#!/usr/bin/env groovy


def props = [
    parameters([string(description: 'CI message', defaultValue: '{}', name: 'CI_MESSAGE')])
]

if (env.BRANCH_NAME == 'master') {
    props.add(properties(
        [pipelineTriggers([[$class: 'CIBuildTrigger', noSquash: true, providerData: [$class: 'FedMsgSubscriberProviderData',name: 'fedora-fedmsg',
         overrides: [topic: 'org.fedoraproject.prod.bodhi.update.status.testing.koji-build-group.build.complete']
        ]]])]
    ))
}

properties(props)

node('master') {

    stage('Init') {
        // checkout scm

        if (env.BRANCH_NAME != 'master') {
            // load test CI message from a file
        }
    }

    stage('Test') {
        // call testing farm and wait
    }

    stage('Archive Results') {
        // call testing farm and wait;
        // wait on master, not on a node :)
    }

    if (env.BRANCH_NAME == 'master') {
        stage('Report on UMB') {
            // ...
        }
    } else {
        stage('Comment on Pull-Request') {
            // ...
        }
    }
}
