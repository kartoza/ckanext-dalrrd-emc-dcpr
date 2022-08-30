import json
import pytest

from ckan.tests import (
    factories,
    helpers,
)
from ckan.logic import NotAuthorized

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "name, private, org_role",
    [
        pytest.param(
            "test_package4",
            True,
            "member",
            marks=pytest.mark.raises(exception=NotAuthorized),
            id="member-cannot-create-package",
        ),
        pytest.param(
            "test-package1", True, "editor", id="editor-can-create-private-package"
        ),
        pytest.param(
            "test-package2",
            False,
            "editor",
            marks=pytest.mark.raises(exception=NotAuthorized),
            id="editor-cannot-create-public-package",
        ),
        pytest.param(
            "test_package3", True, "admin", id="admin-can-create-private-package"
        ),
        pytest.param(
            "test_package3",
            False,
            "admin",
            id="admin-can-create-public-package",
        ),
    ],
)
@pytest.mark.usefixtures(
    "emc_clean_db", "with_plugins", "with_request_context", "emc_create_sasdi_themes"
)
def test_create_package(name, private, org_role):
    user = factories.User()
    owner_organization = factories.Organization()
    helpers.call_action(
        "organization_member_create",
        id=owner_organization["id"],
        username=user["name"],
        role=org_role,
    )
    data_dict = {
        "name": name,
        "private": private,
        "title": name,
        "metadata_standard_name": "standard name",
        "metadata_standard_version": "1.0",
        "notes": f"notes for {name}",
        "purpose": "purpose",
        "status": "completed",
        "metadata_point_of_contact-0-organizational_role": "resource_provider",
        "reference_date": "2020-01-01",
        "iso_topic_category": "biota",
        "owner_org": owner_organization["id"],
        "dataset_language": "en",
        "metadata_language": "en",
        "dataset_character_set": "utf-8",
        "lineage-0-level": "001",
        "lineage-0-lineage_statement": f"lineage statement for {name}",
        "lineage-0-process_step_description": f"lineage description for {name}",
        "distribution-0-distributor_contact": "Surname, name, title",
        "maintainer": "Surname, Name, title.",
        "spatial": json.dumps(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [10.0, 10.0],
                        [10.31, 10.0],
                        [10.31, 10.44],
                        [10.0, 10.44],
                        [10.0, 10.0],
                    ]
                ],
            }
        ),
        "equivalent_scale": "500",
        "spatial_representation_type": "001",
        "spatial_reference_system": "EPSG:4326",
        "metadata_date_stamp": "2020-01-01",
    }

    helpers.call_action(
        "package_create",
        context={"ignore_auth": False, "user": user["name"]},
        **data_dict,
    )


@pytest.mark.parametrize(
    "name, private, org_role",
    [
        pytest.param(
            "test_package5",
            True,
            "editor",
            id="editor-can-update-private-package",
        ),
        pytest.param(
            "test_package6",
            False,
            "editor",
            marks=pytest.mark.raises(exception=NotAuthorized),
            id="editor-cannot-update-public-package",
        ),
    ],
)
@pytest.mark.usefixtures(
    "emc_clean_db", "with_plugins", "with_request_context", "emc_create_sasdi_themes"
)
def test_update_package(name, private, org_role):
    owner_organization = factories.Organization()
    org_admin = factories.User()
    helpers.call_action(
        "organization_member_create",
        id=owner_organization["id"],
        username=org_admin["name"],
        role="admin",
    )
    user = factories.User()
    helpers.call_action(
        "organization_member_create",
        id=owner_organization["id"],
        username=user["name"],
        role=org_role,
    )
    data_dict = {
        "name": name,
        "private": private,
        "title": name,
        "notes": f"notes for {name}",
        "reference_date": "2020-01-01",
        "iso_topic_category": "biota",
        "owner_org": owner_organization["id"],
        "dataset_language": "en",
        "metadata_language": "en",
        "dataset_character_set": "utf-8",
        "lineage": f"lineage for {name}",
        "maintainer": "Surname, Name, title.",
        "spatial": json.dumps(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [10.0, 10.0],
                        [10.31, 10.0],
                        [10.31, 10.44],
                        [10.0, 10.44],
                        [10.0, 10.0],
                    ]
                ],
            }
        ),
        "equivalent_scale": "500",
        "spatial_representation_type": "001",
        "spatial_reference_system": "EPSG:4326",
    }
    helpers.call_action(
        "package_create",
        context={"ignore_auth": False, "user": org_admin["name"]},
        **data_dict,
    )
    patched_notes = f"patched notes"
    helpers.call_action(
        "package_patch",
        context={"ignore_auth": False, "user": user["name"]},
        id=name,
        notes=patched_notes,
    )
