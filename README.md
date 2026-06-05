# rpmdeplint

This repository contains the Fedora-CI test for [rpmdeplint].

[rpmdeplint]: https://github.com/fedora-ci/rpmdeplint/

## Manual execution

To run this test manually simply run the tmt plan providing the following inputs:
- `dist-git-branch` \[context\]: Fedora dist-git branch to run against
- One of the following:
  - `BODHI_UPDATE_ID` \[environment\]: Bodhi update id to test
  - `KOJI_TASK_ID` \[environment\]: Koji task id to test

For example:
```console
$ tmt -c dist-git-branch=rawhide run -a \
  -e BODHI_UPDATE_ID=FEDORA-2025-4c7f2d06f4
$ tmt -c dist-git-branch=rawhide run -a \
  -e KOJI_TASK_ID=43617203
```
