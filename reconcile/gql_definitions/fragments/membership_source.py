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


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union = True
        extra = Extra.forbid


class MembershipProviderSourceV1(ConfiguredBaseModel):
    ...


class AppInterfaceMembershipProviderSourceV1(MembershipProviderSourceV1):
    url: str = Field(..., alias="url")
    username: VaultSecret = Field(..., alias="username")
    password: VaultSecret = Field(..., alias="password")


class MembershipProviderV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    has_audit_trail: bool = Field(..., alias="hasAuditTrail")
    source: Union[
        AppInterfaceMembershipProviderSourceV1, MembershipProviderSourceV1
    ] = Field(..., alias="source")


class RoleMembershipSource(ConfiguredBaseModel):
    group: str = Field(..., alias="group")
    provider: MembershipProviderV1 = Field(..., alias="provider")
