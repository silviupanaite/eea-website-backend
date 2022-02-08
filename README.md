# EEA Main Website backend (Plone 6)

Plone 6 backend for EEA Main website. See also [Plone 6 frontend for EEA Main website](https://github.com/eea/eea-website-frontend).

## Getting started

See [Plone 6 frontend for EEA Main website](https://github.com/eea/eea-website-frontend)

## Try it using Docker

    docker pull eeacms/eea-website-backend
    docker run -it --rm -p 8080:8080 -e SITE=Plone eeacms/eea-website-backend

See Plone backend at http://localhost:8080/Plone

## How to contribute

See [DEVELOP.md](https://github.com/eea/eea-website-backend/blob/master/DEVELOP.md).

## Release

### Automatic release using Jenkins

#### Release flow

The release flow on Plone projects is split in 2 Jenkins jobs:

* A job that runs on every commit on master and creates a production ready GitHub release and tag
* A job that runs on every new tag (including the one created in the first job):
    * A new Docker image is built and released automatically on [DockerHub](https://hub.docker.com/r/eeacms/eea-website-backend) with the release tag.
    * A new entry is automatically added to [EEA Main Website - backend](https://github.com/eea/eea.rancher.catalog/tree/master/templates/eea-website-backend) `EEA Rancher Catalog` with the release tag
    * If the project demo stack is configured in `RANCHER_STACKID`, the demo stack is automatically upgraded to the newly created template version

#### How to start a Production release

*  The automatic release is started by creating a [Pull Request](../../compare/master...develop) from `develop` to `master`. The pull request status checks correlated to the branch and PR Jenkins jobs need to be processed successfully. 1 review from a github user with rights is mandatory.
* It runs on every commit on `master` branch, which is protected from direct commits, only allowing pull request merge commits.
* The automatic release is done by [Jenkins](https://ci.eionet.europa.eu). The status of the release job can be seen both in the `README.md` badges and the green check/red cross/yellow circle near the last commit information. If you click on the icon, you will have the list of checks that were run. The `continuous-integration/jenkins/branch` link goes to the Jenkins job execution webpage.
* Automated release scripts are located in the `eeacms/gitflow` docker image.

## Production

We use [Docker](https://www.docker.com/), [Rancher](https://rancher.com/) and [Jenkins](https://jenkins.io/) to deploy this application in production.

### Deploy

* Within `Rancher > Catalog > EEA` deploy [EEA Main Website - Backend](https://github.com/eea/eea.rancher.catalog/tree/master/templates/eea-website-backend)
* Within `Rancher > Catalog > EEA` deploy [EEA Main Website - Frontend](https://github.com/eea/eea.rancher.catalog/tree/master/templates/eea-website-frontend)

### Upgrade

* Within your Rancher environment click on the `Upgrade available` yellow button next to your stack.
* Confirm the upgrade
* Or roll-back if something went wrong and abort the upgrade procedure.

## Copyright and license

The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

See [LICENSE.md](https://github.com/eea/eea-website-backend/blob/master/LICENSE.md) for details.

## Funding

[European Environment Agency (EU)](http://eea.europa.eu)
