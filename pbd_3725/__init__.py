import os
import uuid

import click

from .artifactory import Artifactory


@click.command()
@click.argument("repository")
@click.option(
    "--path",
    default=None,
    help="Path within the repo to request access to. Defaults to entire repo.",
)
def run_cli(repository, path):
    """Generate an Artifactory access token with access to REPOSITORY."""
    admin_access_token = os.environ["ARTIFACTORY_ADMIN_ACCESS_TOKEN"]
    artifactory = Artifactory(
        "https://lab03.artefacts.tax.service.gov.uk", admin_access_token
    )
    print(f"You wanted access to {repository}, path: {path}.")
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


def get_group_name(repository, path):
    path_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, f"{repository}-{path}")
    return f"build-and-deploy-api-{path_uuid}"
