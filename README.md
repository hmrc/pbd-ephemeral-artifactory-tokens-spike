# pbd-ephemeral-artifactory-tokens-spike

Spike output for [PBD-3725](https://jira.tools.tax.service.gov.uk/browse/PBD-3725).

## Purpose

Demonstrates how we can orchestrate the creation of short lived and narrowly scoped ephemeral access tokens in JFrog Artifactory.

A private B&D API endpoint that requires request signing and is restricted by an appropriate resource policy would invoke a lambda that runs a use case. The use case and gateway code would be informed by the example implementation contained in this repository.

Authentication is assumed to be handled by AWS Gateway, which with AWS_IAM authorization enabled passes an `context.identity.userArn` to the Lambda event. In this example implementation, the ARN, target repository and (optinally) path are defined as command line arguments.

## Prerequisities

* Python 3.10 or above
* Poetry

## Installation

After cloning the repo:

    poetry install

## Usage

Generate an identity token for an administrative artifactory user and store it as an env var called `ARTIFACTORY_ADMIN_ACCESS_TOKEN`.

> Be sure to use one of the newer JFrog platform wide identity/access tokens. A classic style API Key will not be authorised to call some of the API endpoints used by this script.

The syntax of the tool is:

    poetry run get-artifactory-creds [OPTIONS] REPOSITORY ARN

For example, to request an ephemeral token for repository `foo-repo` and ARN `arn:aws:sts::012345678901:assumed-role/foo-ec2-assumable-role/i-0123456789abcdef0`:

    poetry run get-artifactory-creds foo-repo arn:aws:sts::012345678901:assumed-role/foo-ec2-assumable-role/i-0123456789abcdef0

By default, the token will have full access to the repository. You can make the token more granular by specifying a path attribute. This is used as the `includePatterns` on the permission target object. For example:

    poetry run get-artifactory-creds foo-repo arn:aws:sts::012345678901:assumed-role/foo-ec2-assumable-role/i-0123456789abcdef0 --path "bar/baz/**"

It is even possible to set `--path` to a specific file (e.g. `bar/baz/boo.zip`). Because tokens are created without the deploy/override permission, this effectively makes it a one time password (OTP).

Authorisation is controlled by the [config.yml](./config.yml) file at the root of the repo. This controls which ARNs can request access for which repositories and paths.

## Process flow

1. The script determines if the `ARN` supplied is permitted to access the given repository and path. It does this by comparing the account number and role name in the ARN with the [config.yml](./config.yml) in the root of the repo. If no matching permission objects are found, the script exits.
2. The script calculates a name to use for the group and permission target objects that will be created in Artifactory. Because Artifactory only supports group names of 64 characters in length, we use a UUID5 based on the repository name and path to guarantee that we create a consistent name for each combination of repository/path without exceeding that limitation.
3. The script hits the Artifactory API to determine if a group with the calculated name already exists. If it does not, the script makes subsequent calls to create a group and then a permission with appropriate configuration.
4. Finally, the script makes a call to create a token with appropriate configuration that is scoped to the group. The script then outputs the token for the requestor to use in their `PUT` calls.
5. After the expiry period is completed, the token will stop functioning and eventually be cleaned up by Artifactory. The group and permission will be left for subequent calls that require the same level of access, but could safely be housekept.

## Known limitations

* The Artifactory URL is hardcoded to `https://lab03.artefacts.tax.service.gov.uk/`. This is only accessible via the HMRC MDTP VPN.
* The permissions granted to the token are fixed to deploy (write), annotate and read.
* The expiry on the token is fixed to 15 minutes.
* Certain other values, such as object names/descriptions are also hardcoded as per HMRC MDTP requirements.

### License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
