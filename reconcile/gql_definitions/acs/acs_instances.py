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

from reconcile.gql_definitions.fragments.vault_secret import VaultSecret


DEFINITION = """
fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query AcsInstance {
  instances: acs_instance_v1 {
    url
    credentials {
      ... VaultSecret
    }
    authProvider {
      name
      id
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union = True
        extra = Extra.forbid


class AcsInstanceAuthProviderV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    q_id: str = Field(..., alias="id")


class AcsInstanceV1(ConfiguredBaseModel):
    url: str = Field(..., alias="url")
    credentials: VaultSecret = Field(..., alias="credentials")
    auth_provider: AcsInstanceAuthProviderV1 = Field(..., alias="authProvider")


class AcsInstanceQueryData(ConfiguredBaseModel):
    instances: Optional[list[AcsInstanceV1]] = Field(..., alias="instances")


def query(query_func: Callable, **kwargs: Any) -> AcsInstanceQueryData:
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
        AcsInstanceQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return AcsInstanceQueryData(**raw_data)
