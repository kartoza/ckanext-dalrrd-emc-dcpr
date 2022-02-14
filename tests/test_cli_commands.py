import typing

import pytest

from ckan.tests.helpers import CKANCliRunner

from ckanext.dalrrd_emc_dcpr.cli import commands

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "command",
    [
        pytest.param(commands.bootstrap),
        pytest.param(commands.load_sample_data),
        pytest.param(commands.delete_data),
    ],
)
def test_group_commands(command: typing.Callable):
    runner = CKANCliRunner()
    result = runner.invoke(command)
    assert result.exit_code == 0
