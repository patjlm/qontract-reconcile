"""
Generated by qenerate plugin=pydantic_v1. DO NOT MODIFY MANUALLY!
"""
from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611
from datetime import datetime  # noqa: F401 # pylint: disable=W0611
from enum import Enum  # noqa: F401 # pylint: disable=W0611
from typing import (  # noqa: F401 # pylint: disable=W0611
    Any,
    Optional,
    Union,
)

from pydantic import (  # noqa: F401 # pylint: disable=W0611
    BaseModel,
    Extra,
    Field,
    Json,
)

from reconcile.gql_definitions.fragments.jumphost_common_fields import (
    CommonJumphostFields,
)
from reconcile.gql_definitions.fragments.vault_secret import VaultSecret


DEFINITION = """
fragment CommonJumphostFields on ClusterJumpHost_v1 {
  hostname
  knownHosts
  user
  port
  remotePort
  identity {
    ... VaultSecret
  }
}

fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query ClustersMinimal($name: String) {
  clusters: clusters_v1(name: $name) {
    name
    serverUrl
    consoleUrl
    kibanaUrl
    prometheusUrl
    insecureSkipTLSVerify
    jumpHost {
      ... CommonJumphostFields
    }
    managedGroups
    ocm {
      name
    }
    spec {
        private
    }
    automationToken {
      ... VaultSecret
    }
    clusterAdmin
    clusterAdminAutomationToken {
      ... VaultSecret
    }
    internal
    disable {
      integrations
    }
    auth {
      service
      ... on ClusterAuthGithubOrg_v1 {
        org
      }
      ... on ClusterAuthGithubOrgTeam_v1 {
        org
        team
      }
      ... on ClusterAuthOIDC_v1 {
        name
      }
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union = True
        extra = Extra.forbid


class OpenShiftClusterManagerV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")


class ClusterSpecV1(ConfiguredBaseModel):
    private: bool = Field(..., alias="private")


class DisableClusterAutomationsV1(ConfiguredBaseModel):
    integrations: Optional[list[str]] = Field(..., alias="integrations")


class ClusterAuthV1(ConfiguredBaseModel):
    service: str = Field(..., alias="service")


class ClusterAuthGithubOrgV1(ClusterAuthV1):
    org: str = Field(..., alias="org")


class ClusterAuthGithubOrgTeamV1(ClusterAuthV1):
    org: str = Field(..., alias="org")
    team: str = Field(..., alias="team")


class ClusterAuthOIDCV1(ClusterAuthV1):
    name: str = Field(..., alias="name")


class ClusterV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    server_url: str = Field(..., alias="serverUrl")
    console_url: str = Field(..., alias="consoleUrl")
    kibana_url: str = Field(..., alias="kibanaUrl")
    prometheus_url: str = Field(..., alias="prometheusUrl")
    insecure_skip_tls_verify: Optional[bool] = Field(..., alias="insecureSkipTLSVerify")
    jump_host: Optional[CommonJumphostFields] = Field(..., alias="jumpHost")
    managed_groups: Optional[list[str]] = Field(..., alias="managedGroups")
    ocm: Optional[OpenShiftClusterManagerV1] = Field(..., alias="ocm")
    spec: Optional[ClusterSpecV1] = Field(..., alias="spec")
    automation_token: Optional[VaultSecret] = Field(..., alias="automationToken")
    cluster_admin: Optional[bool] = Field(..., alias="clusterAdmin")
    cluster_admin_automation_token: Optional[VaultSecret] = Field(
        ..., alias="clusterAdminAutomationToken"
    )
    internal: Optional[bool] = Field(..., alias="internal")
    disable: Optional[DisableClusterAutomationsV1] = Field(..., alias="disable")
    auth: list[
        Union[
            ClusterAuthGithubOrgTeamV1,
            ClusterAuthGithubOrgV1,
            ClusterAuthOIDCV1,
            ClusterAuthV1,
        ]
    ] = Field(..., alias="auth")


class ClustersMinimalQueryData(ConfiguredBaseModel):
    clusters: Optional[list[ClusterV1]] = Field(..., alias="clusters")


def query(query_func: Callable, **kwargs: Any) -> ClustersMinimalQueryData:
    """
    This is a convenience function which queries and parses the data into
    concrete types. It should be compatible with most GQL clients.
    You do not have to use it to consume the generated data classes.
    Alternatively, you can also mime and alternate the behavior
    of this function in the caller.

    Parameters:
        query_func (Callable): Function which queries your GQL Server
        kwargs: optional arguments that will be passed to the query function

    Returns:
        ClustersMinimalQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return ClustersMinimalQueryData(**raw_data)
