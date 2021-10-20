import pytest

from ckan.tests.helpers import CKANCliRunner

from ..commands.test import test_ckan_cmd

pytestmark = pytest.mark.unit


def test_cli_command():
    runner = CKANCliRunner()
    result = runner.invoke(test_ckan_cmd)
    assert result.output.strip() == "hi there"
