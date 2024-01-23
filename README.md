# rpmdeplint-pipeline

This repository contains the definition of the rpmdeplint CI pipeline.

This pipeline runs the [rpmdeplint](https://github.com/fedora-ci/rpmdeplint-runner) tool on RPM packages and publishes results via [CI Messages](https://pagure.io/fedora-ci/messages).

## Test definition

The generic rpmdeplint test is described in a [Flexible Metadata Format](https://pagure.io/fedora-ci/metadata).

The actual definition lives in the [rpmdeplint.fmf](./rpmdeplint.fmf) file.

## Test execution

The pipeline delegates the test execution to the Testing Farm. The pipeline only collects, archive and report results.

However, it is possible to run the rpmdeplint test locally. To do that, clone this repository and run following command:

```shell
tmt run --all --debug -e RELEASE_ID=f35 -e TASK_ID=62413077
```

The command above will run rpmdeplint on the [utop-2.7.0-3.fc35](https://koji.fedoraproject.org/koji/buildinfo?buildID=1713172) Koji build (it has the task Id "62413077") and it will test it in the context of Fedora 35.

Note you need to have the `tmt-provision-container` package installed on your system.

## Promoting new rpmdeplint image to production

The [rpmdeplint.fmf](./rpmdeplint.fmf) file references a specific version of the container image which contains the rpmdeplint utility.

The version of the image (image tag) is a specific commit hash. By pinning down a specific version, we ensure that:

- we always know what exactly is running in production
- we can easily reproduce reported issues as we can pull the exact image from the container registry
- we can easily rollback, if needed, simply by reverting a commit in this repository

The recommended workflow for promoting a new image to production is as follows:

- build the image the official way
  - open a pull request with your changes in the [rpmdeplint-runner](https://github.com/fedora-ci/rpmdeplint-runner) repository
  - let CI build the test image for you
  - let people review your changes
  - merge once satisfied
  - let CI build the official image for you
    - it will be tagged with the short commit hash of the master branch tip
- open a pull request in this repository and update the image tag in the [rpmdeplint.fmf](./rpmdeplint.fmf)
  - let CI create a test pipeline for you
  - try running some tests with the test pipeline
  - merge once satisfied
- profit; or quickly revert the commit if the new image doesn't work as expected :)
