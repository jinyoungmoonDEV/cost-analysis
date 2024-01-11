import logging

from spaceone.core import cache
from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.auth.jwt.jwt_util import JWTUtil

_LOGGER = logging.getLogger(__name__)


class IdentityManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")
        self.identity_conn: SpaceConnector = self.locator.get_connector(
            SpaceConnector, service="identity"
        )

    def check_workspace(self, workspace_id: str, domain_id: str) -> None:
        system_token = config.get_global("TOKEN")

        self.identity_conn.dispatch(
            "Workspace.check",
            {"workspace_id": workspace_id, "domain_id": domain_id},
            token=system_token,
        )

    @cache.cacheable(
        key="cost-analysis:workspace-name:{domain_id}:{workspace_id}:name", expire=300
    )
    def get_workspace(self, workspace_id: str, domain_id: str) -> str:
        try:
            workspace_info = self.identity_conn.dispatch(
                "Workspace.get",
                {"workspace_id": workspace_id},
                x_domain_id=domain_id,
            )
            return workspace_info["name"]
        except Exception as e:
            _LOGGER.error(f"[get_project_name] API Error: {e}")
            return workspace_id

    def list_service_accounts(self, query: dict, domain_id: str = None) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_conn.dispatch(
                "ServiceAccount.list", {"query": query}, x_domain_id=domain_id
            )
        else:
            return self.identity_conn.dispatch("ServiceAccount.list", {"query": query})

    @cache.cacheable(
        key="cost-analysis:project-name:{domain_id}:{workspace_id}:{project_id}",
        expire=300,
    )
    def get_project_name(self, project_id: str, workspace_id: str, domain_id: str):
        try:
            project_info = self.get_project(project_id, domain_id)
            return project_info["name"]
        except Exception as e:
            _LOGGER.error(f"[get_project_name] API Error: {e}")
            return project_id

    def get_project(self, project_id: str, domain_id: str):
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_conn.dispatch(
                "Project.get", {"project_id": project_id}, x_domain_id=domain_id
            )
        else:
            return self.identity_conn.dispatch(
                "Project.get", {"project_id": project_id}
            )

    def list_projects(self, query: dict, domain_id):
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_conn.dispatch(
                "Project.list", {"query": query}, x_domain_id=domain_id
            )
        else:
            return self.identity_conn.dispatch("Project.list", {"query": query})

    @cache.cacheable(key="cost-analysis:projects-in-pg:{project_group_id}", expire=300)
    def get_projects_in_project_group(self, project_group_id: str):
        params = {
            "query": {
                "only": ["project_id"],
            },
            "project_group_id": project_group_id,
            "include_children": True,
        }

        return self.identity_conn.dispatch("Project.list", params)
