import requests


class Artifactory:
    def __init__(self, url: str, admin_access_token: str) -> None:
        self.url = url
        self.admin_access_token_bearer = f"Bearer {admin_access_token}"

    def check_group_exists(self, group_name: str) -> bool:
        headers = {"Authorization": self.admin_access_token_bearer}
        response = requests.get(
            headers=headers,
            url=f"{self.url}/artifactory/api/security/groups/{group_name}",
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def create_ephemeral_access_token(self, group_name: str) -> str:
        description = f"B&D API generated ephemeral access token with membership of the {group_name} group."
        data = {
            "description": description,
            "expires_in": "300",
            "scope": f"applied-permissions/groups:{group_name}",
            "username": "build-and-deploy-api-ephermal-access-token",
        }
        headers = {
            "Authorization": self.admin_access_token_bearer,
            "Content-Type": "application/json",
        }
        response = requests.post(
            headers=headers, json=data, url=f"{self.url}/access/api/v1/tokens"
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def create_group_with_permission(
        self, group_name: str, repository: str, path: str = None
    ) -> None:
        group_description = (
            "B&D API generated group for use by ephemeral access tokens. "
            f"Allows deploy access to the {repository} repository."
        )
        if path:
            group_description = f"{group_description} Filtered to path '{path}'."
        group_data = {
            "description": group_description,
        }
        group_headers = {
            "Authorization": self.admin_access_token_bearer,
            "Content-Type": "application/vnd.org.jfrog.artifactory.security.User+json",
        }
        group_response = requests.put(
            headers=group_headers,
            json=group_data,
            url=f"{self.url}/artifactory/api/security/groups/{group_name}",
        )
        group_response.raise_for_status()

        permission_data = {
            "name": group_name,
            "repositories": [repository],
            "principals": {
                "groups": {group_name: ["w", "n", "r"]}  # w=deploy, n=annotate, r=read
            },
            "includesPattern": path if path else "**",
        }
        permission_headers = {
            "Authorization": self.admin_access_token_bearer,
            "Content-Type": "application/vnd.org.jfrog.artifactory.security.PermissionTarget+json",
        }
        permission_response = requests.put(
            headers=permission_headers,
            json=permission_data,
            url=f"{self.url}/artifactory/api/security/permissions/{group_name}",
        )
        permission_response.raise_for_status()
