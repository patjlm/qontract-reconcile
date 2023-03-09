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


DEFINITION = """
query VaultPolicies {
    policy: vault_policies_v1 {
        name
        instance {
            name
        }
        rules
    }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union = True
        extra = Extra.forbid


class VaultInstanceV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")


class VaultPolicyV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    instance: VaultInstanceV1 = Field(..., alias="instance")
    rules: str = Field(..., alias="rules")


class VaultPoliciesQueryData(ConfiguredBaseModel):
    policy: Optional[list[VaultPolicyV1]] = Field(..., alias="policy")


def query(query_func: Callable, **kwargs: Any) -> VaultPoliciesQueryData:
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
        VaultPoliciesQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return VaultPoliciesQueryData(**raw_data)
