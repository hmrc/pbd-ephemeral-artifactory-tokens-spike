# pbd-ephemeral-artifactory-tokens-spike

Spike output for [PBD-3725](https://jira.tools.tax.service.gov.uk/browse/PBD-3725).

## Purpose

Demonstrates how we can orchestrate the creation of short lived and narrowly scoped ephemeral access tokens in JFrog Artifactory.

A private B&D API endpoint that requires request signing and is restricted by an appropriate resource policy would invoke a lambda that runs a use case. The use case and gateway could would be informed by the example implementation contained in this repository.

Authentication is assumed to be handled by AWS Gateway, which with AWS_IAM authorization enabled passes an `context.identity.userArn` to the Lambda event.

## Prerequisities

* Python 3.10 or above
* Poetry

## Usage

    poetry run get-artifactory-creds [OPTIONS] REPOSITORY ARN

For example, to request an ephemeral token for repository `foo-repo` and ARN `arn:aws:sts::012345678901:assumed-role/foo-ec2-assumable-role/i-0123456789abcdef0`

    poetry run get-artifactory-creds foo-repo arn:aws:sts::012345678901:assumed-role/foo-ec2-assumable-role/i-0123456789abcdef0

By default, the token will have full access to the repository. You can make the token more granular by specifying a path attribute. This is used as the `includePatterns` on the permission target object. For example:

    poetry run get-artifactory-creds foo-repo arn:aws:sts::012345678901:assumed-role/foo-ec2-assumable-role/i-0123456789abcdef0 --path "bar/baz/**"

Authorisation is controlled by the `config.yml` file at the root of the repo. This controls which ARNs can request access for which repositories and paths.

## Process flow

1. Blah

### License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
