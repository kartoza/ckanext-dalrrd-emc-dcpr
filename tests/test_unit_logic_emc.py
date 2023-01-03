import pkg_resources
import pytest
from unittest import mock

from ckanext.dalrrd_emc_dcpr.logic.action import emc

pytestmark = pytest.mark.unit


@mock.patch("ckanext.dalrrd_emc_dcpr.logic.action.emc.os", autospec=True)
@mock.patch("ckanext.dalrrd_emc_dcpr.logic.action.emc.pkg_resources", autospec=True)
def test_show_version(mock_pkg_resources, mock_os):
    fake_git_sha = "phony git sha"
    fake_version = "phony version"
    mock_os.getenv.return_value = fake_git_sha
    mock_pkg_resources_working_set = mock.MagicMock(pkg_resources.WorkingSet)
    mock_pkg_resources_working_set.version = fake_version
    mock_pkg_resources.require.return_value = [mock_pkg_resources_working_set]
    result = emc.show_version()
    assert result["git_sha"] == fake_git_sha
    assert result["version"] == fake_version
