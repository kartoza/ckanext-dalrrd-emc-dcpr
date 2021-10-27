import pytest

from ckan.tests import (
    factories,
    helpers,
)

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "data_dict, org_role",
    [
        pytest.param({"name": "test-package1"}, "editor"),
    ],
)
@pytest.mark.usefixtures("clean_db", "with_plugins", "with_request_context")
def test_org_editor_can_create_private_package(data_dict, org_role):
    user = factories.User()
    owner_organization = factories.Organization()
    helpers.call_action(
        "organization_member_create",
        data_dict={
            "id": owner_organization.id,
            "username": user["name"],
            "role": org_role,
        },
    )
    data_dict.update(owner_org=owner_organization.id)
    helpers.call_action(
        "package_create",
        context={"ignore_auth": False, "user": user["name"]},
        **data_dict
    )


def test_org_editor_cannot_create_public_package():
    raise NotImplementedError
