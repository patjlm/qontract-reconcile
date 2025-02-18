import sys
from dataclasses import dataclass
from typing import (
    Any,
    Optional,
)
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from reconcile.test.runtime.fixtures import (
    ShardableTestIntegration,
    ShardableTestIntegrationParams,
    SimpleTestIntegration,
)
from reconcile.utils import gql
from reconcile.utils.runtime import runner
from reconcile.utils.runtime.desired_state_diff import DesiredStateDiff
from reconcile.utils.runtime.runner import (
    IntegrationRunConfiguration,
    _integration_dry_run,
    _integration_wet_run,
    _is_task_result_an_error,
    get_desired_state_diff,
    run_integration_cfg,
)


@dataclass
class MockIntegrationRunConfiguration(IntegrationRunConfiguration):
    main_data: dict[str, Any]
    comparison_data: dict[str, Any]

    def main_bundle_desired_state(self) -> dict[str, Any]:
        return self.main_data

    def comparison_bundle_desired_state(self) -> dict[str, Any]:
        return self.comparison_data

    def switch_to_main_bundle(self, validate_schemas: Optional[bool] = None) -> None:
        pass

    def switch_to_comparison_bundle(
        self, validate_schemas: Optional[bool] = None
    ) -> None:
        pass


@pytest.fixture
def dry_run_test_integration_cfg(
    simple_test_integration: SimpleTestIntegration,
) -> IntegrationRunConfiguration:
    return MockIntegrationRunConfiguration(
        integration=simple_test_integration,
        valdiate_schemas=False,
        dry_run=True,
        early_exit_compare_sha="abc",
        check_only_affected_shards=True,
        gql_sha_url=False,
        print_url=True,
        main_data={"data": "a"},
        comparison_data={"data": "b"},
    )


@pytest.fixture
def wet_run_test_integration_cfg(
    simple_test_integration: SimpleTestIntegration,
) -> IntegrationRunConfiguration:
    return MockIntegrationRunConfiguration(
        integration=simple_test_integration,
        valdiate_schemas=False,
        dry_run=False,
        early_exit_compare_sha="abc",
        check_only_affected_shards=True,
        gql_sha_url=False,
        print_url=True,
        main_data={"data": "a"},
        comparison_data={"data": "b"},
    )


def test_run_configuration_switch_to_main_bundle(
    mocker,
    simple_test_integration: SimpleTestIntegration,
):
    gql_init_from_config = mocker.patch.object(gql, "init_from_config")
    cfg = IntegrationRunConfiguration(
        integration=simple_test_integration,
        valdiate_schemas=False,
        dry_run=True,
        early_exit_compare_sha="abc",
        check_only_affected_shards=False,
        gql_sha_url=False,
        print_url=True,
    )
    cfg.switch_to_main_bundle()
    gql_init_from_config.assert_called_with(
        autodetect_sha=False,
        integration=simple_test_integration.name,
        validate_schemas=False,
        print_url=True,
    )


def test_run_configuration_switch_to_comparison_bundle(
    mocker,
    simple_test_integration: SimpleTestIntegration,
):
    gql_init_from_config = mocker.patch.object(gql, "init_from_config")
    gql_init_from_config.return_value = "a"
    cfg = IntegrationRunConfiguration(
        integration=simple_test_integration,
        valdiate_schemas=False,
        dry_run=True,
        early_exit_compare_sha="abc",
        check_only_affected_shards=False,
        gql_sha_url=False,
        print_url=True,
    )
    cfg.switch_to_comparison_bundle()
    gql_init_from_config.assert_called_with(
        sha=cfg.early_exit_compare_sha,
        integration=simple_test_integration.name,
        validate_schemas=False,
        print_url=True,
    )


@pytest.mark.parametrize(
    "check_only_affected_shards,early_exit_sha,previous_data,current_data,desired_state_diff_found,early_exitable,affected_shards",
    [
        # no comparison bundle available, so no early exit and no sharding
        (False, None, {"data": "a"}, {"data": "b"}, False, False, set()),
        # no desired state diff found, so early exit available but no sharding
        (True, "some_sha", {"data": "a"}, {"data": "a"}, True, True, set()),
        # no desired state diff found, so early exit available but no sharding
        (False, "some_sha", {"data": "a"}, {"data": "a"}, True, True, set()),
        # desired state diff found, so no early exit available and also no sharding
        (True, "some_sha", {"data": "a"}, {"data": "b"}, True, False, set()),
        (False, "some_sha", {"data": "a"}, {"data": "b"}, True, False, set()),
        # desired state diff found, so no early exit BUT sharding available
        (
            True,
            "some_sha",
            {"shards": [{"shard": "a", "data": "a"}, {"shard": "b", "data": "b"}]},
            {"shards": [{"shard": "a", "data": "c"}, {"shard": "b", "data": "b"}]},
            True,
            False,
            set("a"),
        ),
        # ... but when check_only_affected_shards is not set, then no sharding
        (
            False,
            "some_sha",
            {"shards": [{"shard": "a", "data": "a"}, {"shard": "b", "data": "b"}]},
            {"shards": [{"shard": "a", "data": "c"}, {"shard": "b", "data": "b"}]},
            True,
            False,
            set(),
        ),
    ],
)
def test_get_desired_state_diff(
    check_only_affected_shards: bool,
    early_exit_sha: Optional[str],
    previous_data: dict[str, Any],
    current_data: dict[str, Any],
    desired_state_diff_found: bool,
    early_exitable: bool,
    affected_shards: set[str],
    shardable_test_integration: ShardableTestIntegration,
):
    cfg = MockIntegrationRunConfiguration(
        integration=shardable_test_integration,
        valdiate_schemas=False,
        dry_run=True,
        early_exit_compare_sha=early_exit_sha,
        check_only_affected_shards=check_only_affected_shards,
        gql_sha_url=False,
        print_url=True,
        main_data=current_data,
        comparison_data=previous_data,
    )
    desired_state_diff = get_desired_state_diff(cfg)
    assert (desired_state_diff is not None) == desired_state_diff_found
    if desired_state_diff:
        assert desired_state_diff.can_exit_early() == early_exitable
        assert desired_state_diff.affected_shards == affected_shards


def test_run_configuration_dispatch_dry_run(
    mocker: MockerFixture,
    simple_test_integration: SimpleTestIntegration,
):
    """
    making sure, the dry run mode is called
    """
    cfg = MockIntegrationRunConfiguration(
        integration=simple_test_integration,
        valdiate_schemas=False,
        dry_run=True,
        early_exit_compare_sha="abc",
        check_only_affected_shards=False,
        gql_sha_url=False,
        print_url=True,
        main_data={"data": "a"},
        comparison_data={"data": "b"},
    )
    integration_wet_run_mock = mocker.patch.object(runner, "_integration_wet_run")
    integration_dry_run_mock = mocker.patch.object(runner, "_integration_dry_run")

    run_integration_cfg(cfg)

    assert not integration_wet_run_mock.called
    assert integration_dry_run_mock.called


def test_run_configuration_dispatch_wet_run(
    mocker: MockerFixture,
    simple_test_integration: SimpleTestIntegration,
):
    """
    making sure, the wet run mode is called
    """
    cfg = MockIntegrationRunConfiguration(
        integration=simple_test_integration,
        valdiate_schemas=False,
        dry_run=False,
        early_exit_compare_sha="abc",
        check_only_affected_shards=False,
        gql_sha_url=False,
        print_url=True,
        main_data={"data": "a"},
        comparison_data={"data": "b"},
    )
    integration_wet_run_mock = mocker.patch.object(runner, "_integration_wet_run")
    integration_dry_run_mock = mocker.patch.object(runner, "_integration_dry_run")

    run_integration_cfg(cfg)

    assert integration_wet_run_mock.called
    assert not integration_dry_run_mock.called


def test_run_configuration_dry_run(
    simple_test_integration: SimpleTestIntegration,
):
    """
    if there is no desired state diff object, we can't say anything about
    early exit or sharding, so the run function of the integration is called
    with dry_run=True
    """
    simple_test_integration.run = MagicMock()  # type: ignore
    _integration_dry_run(
        simple_test_integration,
        None,
    )

    simple_test_integration.run.assert_called_once_with(True)


def test_run_configuration_dry_run_diff_no_early_exit(
    simple_test_integration: SimpleTestIntegration,
):
    """
    when there is not diff, we don't do early exit but run the integration
    """
    simple_test_integration.run = MagicMock()  # type: ignore
    _integration_dry_run(
        simple_test_integration,
        DesiredStateDiff(
            current_desired_state={},
            previous_desired_state={},
            diff_found=True,
            affected_shards=set(),
        ),
    )

    simple_test_integration.run.assert_called_once_with(True)


def test_run_configuration_dry_run_no_diff_early_exit(
    simple_test_integration: SimpleTestIntegration,
):
    """
    when there is no difference in the desired state, exit early.
    """
    simple_test_integration.run = MagicMock()  # type: ignore
    _integration_dry_run(
        simple_test_integration,
        DesiredStateDiff(
            current_desired_state={},
            previous_desired_state={},
            diff_found=False,
            affected_shards=set(),
        ),
    )

    assert not simple_test_integration.run.called


def test_run_configuration_dry_run_diff_no_early_exit_sharding(
    mocker: MockerFixture,
):
    """
    when there is not diff, we don't do early exit. since the integration supports
    sharding, and affected shards have been detected, we run the integration once
    per shard.
    """
    integration_run_func = mocker.patch.object(
        ShardableTestIntegration, "run", autospec=True
    )
    shardable_test_integration = ShardableTestIntegration(
        params=ShardableTestIntegrationParams()
    )
    affected_shards = {"a", "b"}
    _integration_dry_run(
        shardable_test_integration,
        DesiredStateDiff(
            current_desired_state={},
            previous_desired_state={},
            diff_found=True,
            affected_shards=affected_shards,
        ),
    )

    # make sure the run method has been called once per shard
    assert integration_run_func.call_count == len(affected_shards)
    called_sharded_params = [
        c[0][0].params for c in integration_run_func.call_args_list
    ]
    for shard in affected_shards:
        sharded_params = shardable_test_integration.params.copy_and_update(
            {"shard": shard}
        )
        assert sharded_params in called_sharded_params


def test_run_configuration_dry_run_diff_no_early_exit_shard_err(mocker: MockerFixture):
    """
    if a shard fails during dry-run, we expect exit with an error
    """
    succeeding_shard = "succeed"  # success
    another_succeeding_shard = "succeed as well"  # success
    failing_shard = "fail"  # fail
    sys_exit_1_shard = "sys-exit-1"  # fail
    sys_exit_true_shard = "sys-exit-true"  # fail
    sys_exit_0_shard = "sys-exit-0"  # success
    sys_exit_false_shard = "sys-exit-false"  # success

    def integration_run_func(self: ShardableTestIntegration, dry_run: bool) -> None:
        if self.params.shard == failing_shard:
            raise Exception(f"shard {self.params.shard} failed")
        if self.params.shard == sys_exit_1_shard:
            sys.exit(1)
        if self.params.shard == sys_exit_false_shard:
            sys.exit(False)
        if self.params.shard == sys_exit_0_shard:
            sys.exit(0)
        if self.params.shard == sys_exit_true_shard:
            sys.exit(True)

    integration_run_func_mock = mocker.patch.object(
        ShardableTestIntegration, "run", side_effect=integration_run_func, autospec=True
    )

    shardable_test_integration = ShardableTestIntegration(
        params=ShardableTestIntegrationParams()
    )

    affected_shards = {
        succeeding_shard,
        another_succeeding_shard,
        failing_shard,
        sys_exit_1_shard,
        sys_exit_false_shard,
        sys_exit_0_shard,
        sys_exit_true_shard,
    }

    with pytest.raises(SystemExit) as e:
        _integration_dry_run(
            shardable_test_integration,
            DesiredStateDiff(
                current_desired_state={},
                previous_desired_state={},
                diff_found=True,
                affected_shards=affected_shards,
            ),
        )

    # the SystemExit exception contains the nr of failed shards as code
    assert e.value.code == 3

    # make sure the run method has been called once per shard
    assert integration_run_func_mock.call_count == len(affected_shards)
    called_sharded_params = [
        c[0][0].params for c in integration_run_func_mock.call_args_list
    ]
    for shard in affected_shards:
        sharded_params = shardable_test_integration.params.copy_and_update(
            {"shard": shard}
        )
        assert sharded_params in called_sharded_params


def test_run_configuration_wet_run(simple_test_integration: SimpleTestIntegration):
    simple_test_integration.run = MagicMock()  # type: ignore
    _integration_wet_run(
        simple_test_integration,
    )

    assert not simple_test_integration.run.assert_called_once_with(  # type: ignore
        False
    )


#
# test helper for task success
#


@pytest.mark.parametrize(
    "result,expected_is_error",
    [
        # sys.exit(0) and sys.exit(False) are not considered errors
        (SystemExit(0), False),
        (SystemExit(False), False),
        # sys.exit(>1) and sys.exit(True) are considered errors
        (SystemExit(1), True),
        (SystemExit(100), True),
        (SystemExit(True), True),
        # regular exceptions are considered errors
        (Exception("Oh no!"), True),
        # null is not considered an error
        (None, False),
        # any other values are not conidered errors
        (1, False),
        ("some string", False),
    ],
)
def test_is_task_result_an_error(result: Any, expected_is_error: bool):
    assert _is_task_result_an_error(result) == expected_is_error
