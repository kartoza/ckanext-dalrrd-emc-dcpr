import pytest

from ckan.tests.helpers import CKANCliRunner

from .. import commands

pytestmark = pytest.mark.unit


def test_cli_command():
    runner = CKANCliRunner()
    result = runner.invoke(commands.test_ckan_command)
    assert result.output.strip() == "Hi world!"
