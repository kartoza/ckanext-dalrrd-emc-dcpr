import typing

import pytest

from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories, helpers

from ckanext.dalrrd_emc_dcpr.constants import (
    CSI_ORG_NAME,
    NSIF_ORG_NAME,
)
from ckanext.dalrrd_emc_dcpr.model import dcpr_request
from ckanext.dalrrd_emc_dcpr.constants import DCPRRequestStatus

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("emc_clean_db", "with_plugins")
def test_my_dcpr_request_list_auth():
    user = factories.User()
    result = helpers.call_auth(
        "my_dcpr_request_list_auth",
        {
            "user": user["id"],
            "auth_user_obj": model.User.get(user["id"]),
            "model": model,
        },
    )
    assert result is True


@pytest.mark.usefixtures("emc_clean_db", "with_plugins")
def test_my_dcpr_request_list_auth_anonymous():
    with pytest.raises(toolkit.NotAuthorized):
        result = helpers.call_auth(
            "my_dcpr_request_list_auth",
            {
                "user": None,
                "model": model,
            },
        )


@pytest.mark.usefixtures("emc_clean_db", "with_plugins")
def test_dcpr_request_list_public_auth_anonymous():
    result = helpers.call_auth(
        "dcpr_request_list_public_auth",
        {
            "user": None,
            "model": model,
        },
    )
    assert result is True


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_list_pending_auth():
    csi_org = factories.Organization(name=CSI_ORG_NAME)
    nsif_org = factories.Organization(name=NSIF_ORG_NAME)
    nsif_member = factories.User()
    _create_membership(nsif_member, nsif_org)
    csi_member = factories.User()
    _create_membership(csi_member, csi_org)
    registered_user = factories.User()

    base_context = {"model": model}
    test_cases = {
        "csi_member": {
            "additional_context": {
                "user": csi_member["id"],
                "auth_user_obj": model.User.get(csi_member["id"]),
            },
            "auth_functions": [
                ("dcpr_request_list_pending_csi_auth", True),
                ("dcpr_request_list_pending_nsif_auth", False),
            ],
        },
        "nsif_member": {
            "additional_context": {
                "user": nsif_member["id"],
                "auth_user_obj": model.User.get(nsif_member["id"]),
            },
            "auth_functions": [
                ("dcpr_request_list_pending_nsif_auth", True),
                ("dcpr_request_list_pending_csi_auth", False),
            ],
        },
        "registered": {
            "additional_context": {
                "user": registered_user["id"],
                "auth_user_obj": model.User.get(registered_user["id"]),
            },
            "auth_functions": [
                ("dcpr_request_list_pending_nsif_auth", False),
                ("dcpr_request_list_pending_csi_auth", False),
            ],
        },
        "anonymous": {
            "additional_context": {"user": None},
            "auth_functions": [
                ("dcpr_request_list_pending_nsif_auth", False),
                ("dcpr_request_list_pending_csi_auth", False),
            ],
        },
    }
    for role, role_items in test_cases.items():
        context = base_context.copy()
        context.update(role_items["additional_context"])
        for auth_function_name, expected in role_items["auth_functions"]:
            if expected is True:
                result = helpers.call_auth(auth_function_name, context)
                assert result is expected
            else:
                with pytest.raises(toolkit.NotAuthorized):
                    helpers.call_auth(auth_function_name, context)


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_create_auth():
    user = factories.User()
    org = factories.Organization()
    _create_membership(user, org)
    result = helpers.call_auth(
        "dcpr_request_create_auth",
        {
            "model": model,
            "user": user["id"],
            "auth_user_obj": model.User.get(user["id"]),
        },
    )
    assert result is True


@pytest.mark.usefixtures("emc_clean_db", "with_plugins")
def test_dcpr_request_create_auth_anonymous():
    with pytest.raises(toolkit.NotAuthorized):
        helpers.call_auth("dcpr_request_create_auth", {"model": model, "user": None})


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_show_auth():
    (
        owner_user,
        nsif_member,
        nsif_reviewer,
        csi_member,
        csi_reviewer,
        registered_user,
        dcpr_request_obj,
    ) = _prepare_dcpr_request_auth_test_items()
    test_cases = {
        "owner": {
            "additional_context": {
                "user": owner_user["id"],
                "auth_user_obj": model.User.get(owner_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, True),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, True),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, True),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, True),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, True),
            ],
        },
        "nsif_member": {
            "additional_context": {
                "user": nsif_member["id"],
                "auth_user_obj": model.User.get(nsif_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, True),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, True),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, True),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
            ],
        },
        "csi_member": {
            "additional_context": {
                "user": csi_member["id"],
                "auth_user_obj": model.User.get(csi_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, True),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, True),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, True),
                (DCPRRequestStatus.ACCEPTED, True),
                (DCPRRequestStatus.REJECTED, True),
            ],
        },
        "registered": {
            "additional_context": {
                "user": registered_user["id"],
                "auth_user_obj": model.User.get(registered_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
            ],
        },
        "anonymous": {
            "additional_context": {"user": None},
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, True),
                (DCPRRequestStatus.REJECTED, True),
            ],
        },
    }
    _test_dcpr_request_auth_function(
        "dcpr_request_show_auth", dcpr_request_obj, test_cases
    )


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_update_by_owner_auth():
    (
        owner_user,
        nsif_member,
        nsif_reviewer,
        csi_member,
        csi_reviewer,
        registered_user,
        dcpr_request_obj,
    ) = _prepare_dcpr_request_auth_test_items()
    test_cases = {
        "owner": {
            "additional_context": {
                "user": owner_user["id"],
                "auth_user_obj": model.User.get(owner_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, True),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "nsif_member": {
            "additional_context": {
                "user": nsif_member["id"],
                "auth_user_obj": model.User.get(nsif_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "csi_member": {
            "additional_context": {
                "user": csi_member["id"],
                "auth_user_obj": model.User.get(csi_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "registered": {
            "additional_context": {
                "user": registered_user["id"],
                "auth_user_obj": model.User.get(registered_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "anonymous": {
            "additional_context": {"user": None},
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
    }
    _test_dcpr_request_auth_function(
        "dcpr_request_update_by_owner_auth", dcpr_request_obj, test_cases
    )


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_update_by_nsif_auth():
    (
        owner_user,
        nsif_member,
        nsif_reviewer,
        csi_member,
        csi_reviewer,
        registered_user,
        dcpr_request_obj,
    ) = _prepare_dcpr_request_auth_test_items()
    test_cases = {
        "owner": {
            "additional_context": {
                "user": owner_user["id"],
                "auth_user_obj": model.User.get(owner_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "nsif_member": {
            "additional_context": {
                "user": nsif_member["id"],
                "auth_user_obj": model.User.get(nsif_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "nsif_reviewer": {
            "additional_context": {
                "user": nsif_reviewer["id"],
                "auth_user_obj": model.User.get(nsif_reviewer["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, True),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "csi_member": {
            "additional_context": {
                "user": csi_member["id"],
                "auth_user_obj": model.User.get(csi_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "csi_reviewer": {
            "additional_context": {
                "user": csi_reviewer["id"],
                "auth_user_obj": model.User.get(csi_reviewer["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "registered": {
            "additional_context": {
                "user": registered_user["id"],
                "auth_user_obj": model.User.get(registered_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "anonymous": {
            "additional_context": {"user": None},
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
    }
    _test_dcpr_request_auth_function(
        "dcpr_request_update_by_nsif_auth", dcpr_request_obj, test_cases
    )


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_update_by_csi_auth():
    (
        owner_user,
        nsif_member,
        nsif_reviewer,
        csi_member,
        csi_reviewer,
        registered_user,
        dcpr_request_obj,
    ) = _prepare_dcpr_request_auth_test_items()
    test_cases = {
        "owner": {
            "additional_context": {
                "user": owner_user["id"],
                "auth_user_obj": model.User.get(owner_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "nsif_member": {
            "additional_context": {
                "user": nsif_member["id"],
                "auth_user_obj": model.User.get(nsif_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "nsif_reviewer": {
            "additional_context": {
                "user": nsif_reviewer["id"],
                "auth_user_obj": model.User.get(nsif_reviewer["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "csi_member": {
            "additional_context": {
                "user": csi_member["id"],
                "auth_user_obj": model.User.get(csi_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "csi_reviewer": {
            "additional_context": {
                "user": csi_reviewer["id"],
                "auth_user_obj": model.User.get(csi_reviewer["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, True),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "registered": {
            "additional_context": {
                "user": registered_user["id"],
                "auth_user_obj": model.User.get(registered_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "anonymous": {
            "additional_context": {"user": None},
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
    }
    _test_dcpr_request_auth_function(
        "dcpr_request_update_by_csi_auth", dcpr_request_obj, test_cases
    )


@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_dcpr_request_submit_auth():
    (
        owner_user,
        nsif_member,
        nsif_reviewer,
        csi_member,
        csi_reviewer,
        registered_user,
        dcpr_request_obj,
    ) = _prepare_dcpr_request_auth_test_items()
    test_cases = {
        "owner": {
            "additional_context": {
                "user": owner_user["id"],
                "auth_user_obj": model.User.get(owner_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, True),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, True),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "nsif_member": {
            "additional_context": {
                "user": nsif_member["id"],
                "auth_user_obj": model.User.get(nsif_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "csi_member": {
            "additional_context": {
                "user": csi_member["id"],
                "auth_user_obj": model.User.get(csi_member["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "registered": {
            "additional_context": {
                "user": registered_user["id"],
                "auth_user_obj": model.User.get(registered_user["id"]),
            },
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
        "anonymous": {
            "additional_context": {"user": None},
            "statuses": [
                (DCPRRequestStatus.UNDER_PREPARATION, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF, False),
                (DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI, False),
                (DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
                (DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
                (DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
                (DCPRRequestStatus.UNDER_CSI_REVIEW, False),
                (DCPRRequestStatus.ACCEPTED, False),
                (DCPRRequestStatus.REJECTED, False),
            ],
        },
    }
    _test_dcpr_request_auth_function(
        "dcpr_request_submit_auth", dcpr_request_obj, test_cases
    )


def _create_membership(
    user: typing.Dict, organization: typing.Dict, role: typing.Optional[str] = "member"
):
    toolkit.get_action("organization_member_create")(
        context={
            "ignore_auth": True,
            "user": user["id"],
        },
        data_dict={
            "id": organization["id"],
            "username": user["name"],
            "role": role,
        },
    )


def _change_dcpr_request_status(
    dcpr_request_obj: dcpr_request.DCPRRequest, target_status: DCPRRequestStatus
) -> dcpr_request.DCPRRequest:
    dcpr_request_obj.status = target_status.value
    model.meta.Session.commit()
    return dcpr_request_obj


def _change_request_nsif_reviewer(request: typing.Dict, new_reviewer_id: str):
    request_obj = dcpr_request.DCPRRequest.get(request["csi_reference_id"])
    request_obj.nsif_reviewer = new_reviewer_id
    model.meta.Session.commit()
    return request_obj


def _change_request_csi_reviewer(request: typing.Dict, new_reviewer_id: str):
    request_obj = dcpr_request.DCPRRequest.get(request["csi_reference_id"])
    request_obj.csi_moderator = new_reviewer_id
    model.meta.Session.commit()
    return request_obj


def _get_dcpr_request(user, organization):
    return toolkit.get_action("dcpr_request_create")(
        context={"user": user["name"]},
        data_dict={
            "proposed_project_name": f"test",
            "capture_start_date": "2022-01-01",
            "capture_end_date": "2022-01-02",
            "cost": "200000",
            "organization_id": organization["id"],
            "organisation_level": "national",
            "spatial_resolution": "1/3000",
            "contact_person_name": "contact1",
            "datasets": [
                {
                    "proposed_dataset_title": "dummy",
                    "dataset_purpose": "dummy",
                    "lineage_statement": "lineage statement",
                    "proposed_abstract": "proposed abstract",
                    "topic_category": "farming",
                    "metadata_characterset": "ucs-2",
                    "dataset_characterset": "ucs-2",
                    "data_type": "001",
                }
            ],
        },
    )


def _prepare_dcpr_request_auth_test_items():
    nsif_org = factories.Organization(name=NSIF_ORG_NAME)
    nsif_member = factories.User()
    nsif_reviewer = factories.User()
    _create_membership(nsif_member, nsif_org)
    _create_membership(nsif_reviewer, nsif_org)

    csi_org = factories.Organization(name=CSI_ORG_NAME)
    csi_member = factories.User()
    csi_reviewer = factories.User()
    _create_membership(csi_member, csi_org)
    _create_membership(csi_reviewer, csi_org)

    owner_user = factories.User()
    owner_org = factories.Organization()
    _create_membership(owner_user, owner_org)

    registered_user = factories.User()

    created = _get_dcpr_request(owner_user, owner_org)
    _change_request_nsif_reviewer(created, nsif_reviewer["id"])
    dcpr_request_obj = _change_request_csi_reviewer(created, csi_reviewer["id"])

    return (
        owner_user,
        nsif_member,
        nsif_reviewer,
        csi_member,
        csi_reviewer,
        registered_user,
        dcpr_request_obj,
    )


def _test_dcpr_request_auth_function(auth_function_name, dcpr_request_obj, test_cases):
    # NOTE: because it is very costly to clean the DB after every test case has run
    # we are defining the various test cases inside a single function and run them
    # together - this means a bit less visibility on the running test, but greatly
    # improves test execution times
    base_context = {"model": model, "user": None}
    for role, role_params in test_cases.items():
        context = base_context.copy()
        context.update(role_params["additional_context"])
        for status, expected in role_params["statuses"]:
            print(f"testing {role=} {status=} {expected}...")
            _change_dcpr_request_status(dcpr_request_obj, status)
            if expected:
                result = helpers.call_auth(
                    auth_function_name,
                    context,
                    csi_reference_id=dcpr_request_obj.csi_reference_id,
                )
                assert result is expected
            else:
                with pytest.raises(toolkit.NotAuthorized):
                    helpers.call_auth(
                        auth_function_name,
                        context,
                        csi_reference_id=dcpr_request_obj.csi_reference_id,
                    )
