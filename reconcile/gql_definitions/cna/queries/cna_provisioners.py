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

from reconcile.gql_definitions.fragments.ocm_environment import OCMEnvironment
from reconcile.gql_definitions.fragments.vault_secret import VaultSecret


DEFINITION = """
fragment OCMEnvironment on OpenShiftClusterManagerEnvironment_v1 {
    name
    url
    accessTokenClientId
    accessTokenUrl
    accessTokenClientSecret {
        ... VaultSecret
    }
}

fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query CNAProvisioners {
  cna_provisioners: cna_experimental_provisioners_v1 {
    name
    description
    ocm {
      name
      orgId
      accessTokenUrl
      accessTokenClientId
      accessTokenClientSecret {
        ... VaultSecret
      }
      environment {
        ... OCMEnvironment
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
    org_id: str = Field(..., alias="orgId")
    access_token_url: Optional[str] = Field(..., alias="accessTokenUrl")
    access_token_client_id: Optional[str] = Field(..., alias="accessTokenClientId")
    access_token_client_secret: Optional[VaultSecret] = Field(
        ..., alias="accessTokenClientSecret"
    )
    environment: OCMEnvironment = Field(..., alias="environment")


class CNAExperimentalProvisionerV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    description: Optional[str] = Field(..., alias="description")
    ocm: OpenShiftClusterManagerV1 = Field(..., alias="ocm")


class CNAProvisionersQueryData(ConfiguredBaseModel):
    cna_provisioners: Optional[list[CNAExperimentalProvisionerV1]] = Field(
        ..., alias="cna_provisioners"
    )


def query(query_func: Callable, **kwargs: Any) -> CNAProvisionersQueryData:
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
        CNAProvisionersQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return CNAProvisionersQueryData(**raw_data)
