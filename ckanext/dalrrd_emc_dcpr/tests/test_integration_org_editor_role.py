import pytest

from ckan.tests import (
    factories,
    helpers,
)
from ckan.logic import NotAuthorized

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "data_dict, org_role",
    [
        pytest.param(
            {"name": "test_package4"},
            "member",
            marks=pytest.mark.raises(exception=NotAuthorized),
            id="member-cannot-create-package",
        ),
        pytest.param(
            {"name": "test-package1"}, "editor", id="editor-can-create-private-package"
        ),
        pytest.param(
            {"name": "test-package2", "private": "false"},
            "editor",
            marks=pytest.mark.raises(exception=NotAuthorized),
            id="editor-cannot-create-public-package",
        ),
        pytest.param(
            {"name": "test_package3"}, "admin", id="admin-can-create-private-package"
        ),
        pytest.param(
            {"name": "test_package3", "private": "false"},
            "admin",
            id="admin-can-create-public-package",
        ),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_create_package(data_dict, org_role):
    user = factories.User()
    owner_organization = factories.Organization()
    helpers.call_action(
        "organization_member_create",
        id=owner_organization["id"],
        username=user["name"],
        role=org_role,
    )
    data_dict.update(owner_org=owner_organization["id"])
    helpers.call_action(
        "package_create",
        context={"ignore_auth": False, "user": user["name"]},
        **data_dict
    )
