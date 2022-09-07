import os
import uuid

from typing import Tuple

import click
import yaml

from .artifactory import Artifactory


@click.command()
@click.argument("repository")
@click.argument("arn")
@click.option(
    "--path",
    default="**",
    help="Path within the repo to request access to. Defaults to entire repo.",
)
def run_cli(repository: str, arn: str, path: str) -> None:
    """Generate an Artifactory access token with access to REPOSITORY as ARN."""
    admin_access_token = os.environ["ARTIFACTORY_ADMIN_ACCESS_TOKEN"]
    artifactory = Artifactory(
        "https://lab03.artefacts.tax.service.gov.uk", admin_access_token
    )
    print(f"You wanted access to {repository}, path: {path}.")
    account_id, iam_role_name = get_aws_account_and_role(arn)
    if check_permissions(account_id, iam_role_name, repository, path):
        print(
            f"Principal {arn} has permission to request tokens for {repository}/{path}."
        )
    else:
        print(
            f"Principal {arn} does not have permission to request tokens for {repository}/{path}."
        )
        exit(1)
    group_name = get_group_name(repository, path)
    print(f"The group name will be {group_name}.")
    if not artifactory.check_group_exists(group_name):
        print("The group does not exist, creating it and a permission now.")
        artifactory.create_group_with_permission(group_name, repository, path)
    else:
        print("The group already exists.")
    print(f"Creating an ephameral access token with membership of the group.")
    ephemeral_access_token = artifactory.create_ephemeral_access_token(group_name)
    print(f"Your ephemeral access token is: {ephemeral_access_token}")


def check_permissions(
    account_id: str, iam_role_name: str, repository: str, path: str
) -> bool:
    with open("./config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)
    try:
        permissions = config["accounts"][account_id]["roles"][iam_role_name][
            "permissions"
        ]
    except KeyError:
        return False
    for permission in permissions:
        if permission["repository"] == repository and path.startswith(
            permission["path"]
        ):
            return True
    return False


def get_group_name(repository: str, path: str) -> str:
    path_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, f"{repository}-{path}")
    return f"build-and-deploy-api-{path_uuid}"


def get_aws_account_and_role(arn: str) -> Tuple[str, str]:
    arn_parts = arn.split("/")
    account_id = arn_parts[0].split(":")[4]
    iam_role_name = arn_parts[1]
    return account_id, iam_role_name
