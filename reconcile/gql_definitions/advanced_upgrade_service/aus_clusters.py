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

from reconcile.gql_definitions.fragments.aus_organization import AUSOCMOrganization
from reconcile.gql_definitions.fragments.upgrade_policy import ClusterUpgradePolicy


DEFINITION = """
fragment AUSOCMOrganization on OpenShiftClusterManager_v1 {
  name
  environment {
    ... OCMEnvironment
  }
  orgId
  accessTokenClientId
  accessTokenUrl
  accessTokenClientSecret {
    ... VaultSecret
  }
  blockedVersions
  addonManagedUpgrades
  addonUpgradeTests {
    addon {
      name
    }
    instance {
      name
      token {
        ... VaultSecret
      }
    }
    name
  }
  inheritVersionData {
    name
    publishVersionData {
      name
    }
  }
  sectors {
    name
    dependencies {
      name
      ocm {
        name
      }
    }
  }
  upgradePolicyAllowedWorkloads
  upgradePolicyClusters {
    name
    upgradePolicy {
      ... ClusterUpgradePolicy
    }
  }
}

fragment ClusterUpgradePolicy on ClusterUpgradePolicy_v1 {
  workloads
  schedule
  conditions {
    mutexes
    soakDays
    sector
  }
}

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

query AUSClusters($name: String) {
  clusters: clusters_v1(name: $name) {
    name
    ocm {
        ... AUSOCMOrganization
    }
    upgradePolicy {
        ... ClusterUpgradePolicy
    }
    spec {
        product
    }
    disable {
        integrations
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union = True
        extra = Extra.forbid


class ClusterSpecV1(ConfiguredBaseModel):
    product: str = Field(..., alias="product")


class DisableClusterAutomationsV1(ConfiguredBaseModel):
    integrations: Optional[list[str]] = Field(..., alias="integrations")


class ClusterV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    ocm: Optional[AUSOCMOrganization] = Field(..., alias="ocm")
    upgrade_policy: Optional[ClusterUpgradePolicy] = Field(..., alias="upgradePolicy")
    spec: Optional[ClusterSpecV1] = Field(..., alias="spec")
    disable: Optional[DisableClusterAutomationsV1] = Field(..., alias="disable")


class AUSClustersQueryData(ConfiguredBaseModel):
    clusters: Optional[list[ClusterV1]] = Field(..., alias="clusters")


def query(query_func: Callable, **kwargs: Any) -> AUSClustersQueryData:
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
        AUSClustersQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return AUSClustersQueryData(**raw_data)
