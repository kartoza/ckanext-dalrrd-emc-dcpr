import typing

import pytest

from ckan.model import User, Group, meta
from ckan.plugins import toolkit
from ckan.tests import factories, helpers

from ckanext.dalrrd_emc_dcpr.constants import (
    CSI_ORG_NAME,
    NSIF_ORG_NAME,
)
from ckanext.dalrrd_emc_dcpr.model import dcpr_request
from ckanext.dalrrd_emc_dcpr.constants import DCPRRequestStatus

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "target_status, should_be_public",
    [
        pytest.param(DCPRRequestStatus.UNDER_PREPARATION, False),
        pytest.param(DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
        pytest.param(DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
        pytest.param(DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
        pytest.param(DCPRRequestStatus.UNDER_CSI_REVIEW, False),
        pytest.param(DCPRRequestStatus.ACCEPTED, True),
        pytest.param(DCPRRequestStatus.REJECTED, True),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_list_public_dcpr_requests(target_status, should_be_public):
    dcpr_request_data_dict = {
        "proposed_project_name": f"test-status-{target_status.value}",
        "capture_start_date": "2022-01-01",
        "capture_end_date": "2022-01-02",
        "cost": "200000",
        "datasets": [
            {
                "proposed_dataset_title": "dummy",
                "dataset_purpose": "dummy",
            }
        ],
    }
    user = factories.User()
    organization = factories.Organization()
    toolkit.get_action("organization_member_create")(
        context={
            "ignore_auth": True,
            "user": user["id"],
        },
        data_dict={
            "id": organization["id"],
            "username": user["name"],
            "role": "member",
        },
    )
    # helpers.call_action(
    #     "organization_member_create",
    #     id=organization["id"],
    #     username=user["name"],
    #     role="member",
    # )
    dcpr_request_data_dict["organization_id"] = organization["id"]

    created = toolkit.get_action("dcpr_request_create")(
        context={"user": user["name"]}, data_dict=dcpr_request_data_dict
    )

    # created = helpers.call_action(
    #     "dcpr_request_create",
    #     context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
    #     **dcpr_request_data_dict,
    # )
    print(f"{created=}")
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    print(f"{request_obj=}")
    meta.Session.commit()
    # public_records = helpers.call_action("dcpr_request_list_public")
    public_records = toolkit.get_action("dcpr_request_list_public")()
    print(f"{public_records=}")
    if should_be_public:
        assert len(public_records) == 1
        assert public_records[0]["csi_reference_id"] == request_obj.csi_reference_id
    else:
        assert len(public_records) == 0


@pytest.mark.parametrize(
    "target_status",
    [
        pytest.param(DCPRRequestStatus.UNDER_PREPARATION),
        pytest.param(DCPRRequestStatus.AWAITING_NSIF_REVIEW),
        pytest.param(DCPRRequestStatus.UNDER_NSIF_REVIEW),
        pytest.param(DCPRRequestStatus.AWAITING_CSI_REVIEW),
        pytest.param(DCPRRequestStatus.UNDER_CSI_REVIEW),
        pytest.param(DCPRRequestStatus.ACCEPTED),
        pytest.param(DCPRRequestStatus.REJECTED),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_list_my_dcpr_requests(target_status):
    user = factories.User()
    organization = factories.Organization()
    toolkit.get_action("organization_member_create")(
        context={
            "ignore_auth": True,
            "user": user["id"],
        },
        data_dict={
            "id": organization["id"],
            "username": user["name"],
            "role": "member",
        },
    )
    # helpers.call_action(
    #     "organization_member_create",
    #     id=organization["id"],
    #     username=user["name"],
    #     role="member",
    # )
    dcpr_request_data_dict = {
        "proposed_project_name": f"test-{target_status.value}",
        "capture_start_date": "2022-01-01",
        "capture_end_date": "2022-01-02",
        "cost": "200000",
        "organization_id": organization["id"],
        "datasets": [
            {
                "proposed_dataset_title": "dummy",
                "dataset_purpose": "dummy",
            }
        ],
    }
    created = toolkit.get_action("dcpr_request_create")(
        context={"user": user["name"]}, data_dict=dcpr_request_data_dict
    )
    # created = helpers.call_action(
    #     "dcpr_request_create",
    #     context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
    #     **dcpr_request_data_dict,
    # )
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    print(f"{request_obj=}")
    meta.Session.commit()
    my_requests = toolkit.get_action("my_dcpr_request_list")(
        context={"user": user["name"]}
    )
    # my_requests = helpers.call_action(
    #     "my_dcpr_request_list",
    #     context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
    # )
    print(f"{my_requests=}")
    assert len(my_requests) == 1
    assert my_requests[0]["csi_reference_id"] == request_obj.csi_reference_id


@pytest.mark.parametrize(
    "is_org_member, is_sysadmin",
    [
        pytest.param(True, False),
        pytest.param(False, True),
        pytest.param(False, False),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_create_dcpr_request(is_org_member, is_sysadmin):
    organization = factories.Organization()
    dcpr_request_data_dict = {
        "proposed_project_name": f"test",
        "capture_start_date": "2022-01-01",
        "capture_end_date": "2022-01-02",
        "cost": "200000",
        "organization_id": organization["id"],
        "datasets": [
            {
                "proposed_dataset_title": "dummy",
                "dataset_purpose": "dummy",
            }
        ],
    }
    if is_org_member:
        user = factories.User()
        toolkit.get_action("organization_member_create")(
            context={
                "ignore_auth": True,
                "user": user["id"],
            },
            data_dict={
                "id": organization["id"],
                "username": user["name"],
                "role": "member",
            },
        )
        # helpers.call_action(
        #     "organization_member_create",
        #     id=organization["id"],
        #     username=user["name"],
        #     role="member",
        # )
        context = {"user": user["name"], "auth_user_obj": User.get(user["id"])}
    elif is_sysadmin:
        user = factories.User(sysadmin=True)
        context = {"user": user["name"], "auth_user_obj": User.get(user["id"])}
    else:
        user = factories.User()
        context = {"user": user["name"], "auth_user_obj": User.get(user["id"])}
    toolkit.get_action("dcpr_request_create")(
        context=context, data_dict=dcpr_request_data_dict
    )
    # helpers.call_action(
    #     "dcpr_request_create", context=context, **dcpr_request_data_dict
    # )


@pytest.mark.parametrize(
    "target_status, should_succeed",
    [
        pytest.param(DCPRRequestStatus.UNDER_PREPARATION, True),
        pytest.param(DCPRRequestStatus.AWAITING_NSIF_REVIEW, False),
        pytest.param(DCPRRequestStatus.UNDER_NSIF_REVIEW, False),
        pytest.param(DCPRRequestStatus.AWAITING_CSI_REVIEW, False),
        pytest.param(DCPRRequestStatus.UNDER_CSI_REVIEW, False),
        pytest.param(DCPRRequestStatus.ACCEPTED, False),
        pytest.param(DCPRRequestStatus.REJECTED, False),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_delete_dcpr_request(target_status, should_succeed):
    user = factories.User()
    organization = factories.Organization()
    _create_membership(user, organization)
    created = _get_dcpr_request(user, organization)
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    meta.Session.commit()
    action = toolkit.get_action("dcpr_request_delete")
    if should_succeed:
        action(
            context={"user": user["name"]},
            data_dict={"csi_reference_id": created["csi_reference_id"]},
        )
        with pytest.raises(toolkit.ObjectNotFound):
            toolkit.get_action("dcpr_request_show")(
                context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
                data_dict={
                    "csi_reference_id": created["csi_reference_id"],
                },
            )
    else:
        with pytest.raises(toolkit.NotAuthorized):
            action(
                context={"user": user["name"]},
                data_dict={"csi_reference_id": created["csi_reference_id"]},
            )


@pytest.mark.parametrize(
    "update_action, target_status, actor, should_succeed, update_field, update_value",
    [
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "proposed_project_name",
            "my updated name",
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "capture_start_date",
            "2022-12-31",
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "capture_end_date",
            "2023-02-01",
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "additional_project_context",
            "updated project context",
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "cost",
            12345,
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "spatial_resolution",
            "10",
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            True,
            "additional_information",
            "updated additional information",
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.ACCEPTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_owner",
            DCPRRequestStatus.REJECTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.UNDER_PREPARATION,
            "nsif_member",
            False,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "nsif_member",
            True,
            "nsif_review_notes",
            "updated nsif notes",
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "nsif_member",
            False,
            "csi_moderation_notes",
            "updated csi notes",
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "nsif_member",
            False,
            "proposed_project_name",
            "updated name",
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.ACCEPTED,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_nsif",
            DCPRRequestStatus.REJECTED,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.UNDER_PREPARATION,
            "csi_member",
            False,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "csi_member",
            True,
            "csi_moderation_notes",
            "updated csi notes",
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "csi_member",
            False,
            "nsif_review_notes",
            "updated nsif notes",
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "csi_member",
            False,
            "proposed_project_name",
            "updated name",
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.ACCEPTED,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "dcpr_request_update_by_csi",
            DCPRRequestStatus.REJECTED,
            "csi_member",
            False,
            None,
            None,
        ),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_update_dcpr_request(
    update_action, target_status, actor, should_succeed, update_field, update_value
):
    owner_user = factories.User()
    owner_organization = factories.Organization()
    _create_membership(owner_user, owner_organization)
    nsif_org = factories.Organization(NSIF_ORG_NAME)
    nsif_member = factories.User()
    _create_membership(nsif_member, nsif_org)
    csi_org = factories.Organization(CSI_ORG_NAME)
    csi_member = factories.User()
    _create_membership(csi_member, csi_org)
    created = _get_dcpr_request(owner_user, owner_organization)
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    if target_status == DCPRRequestStatus.UNDER_NSIF_REVIEW:
        request_obj.nsif_reviewer = nsif_member
    elif target_status == DCPRRequestStatus.UNDER_CSI_REVIEW:
        request_obj.csi_moderator = csi_member
    meta.Session.commit()
    action = toolkit.get_action(update_action)
    action_data_dict = {
        "csi_reference_id": created["csi_reference_id"],
        update_field: update_value,
    }
    action_context = {}
    if actor == "owner":
        action_context["user"] = owner_user["name"]
    elif actor == "nsif_member":
        action_context["user"] = nsif_member["name"]
    elif actor == "csi_member":
        action_context["user"] = csi_member["name"]
    elif actor == "anonymous":
        pass
    elif actor == "other":
        another_user = factories.User()
        action_context["user"] = another_user["name"]
    if should_succeed:
        action(context=action_context, data_dict=action_data_dict)
        updated = toolkit.get_action("dcpr_request_show")(
            context={
                "user": owner_user["name"],
                "auth_user_obj": User.get(owner_user["id"]),
            },
            data_dict={"csi_reference_id": created["csi_reference_id"]},
        )
        assert updated[update_field] == update_value
    else:
        with pytest.raises(toolkit.NotAuthorized):
            action(context=action_context, data_dict=action_data_dict)


@pytest.mark.parametrize(
    "target_status, actor, should_succeed",
    [
        pytest.param(DCPRRequestStatus.UNDER_PREPARATION, "owner", True),
        pytest.param(DCPRRequestStatus.UNDER_PREPARATION, "anonymous", False),
        pytest.param(DCPRRequestStatus.UNDER_PREPARATION, "other", False),
        pytest.param(DCPRRequestStatus.AWAITING_NSIF_REVIEW, "owner", False),
        pytest.param(DCPRRequestStatus.AWAITING_NSIF_REVIEW, "anonymous", False),
        pytest.param(DCPRRequestStatus.AWAITING_NSIF_REVIEW, "other", False),
        pytest.param(DCPRRequestStatus.UNDER_NSIF_REVIEW, "owner", False),
        pytest.param(DCPRRequestStatus.UNDER_NSIF_REVIEW, "anonymous", False),
        pytest.param(DCPRRequestStatus.UNDER_NSIF_REVIEW, "other", False),
        pytest.param(DCPRRequestStatus.AWAITING_CSI_REVIEW, "owner", False),
        pytest.param(DCPRRequestStatus.AWAITING_CSI_REVIEW, "anonymous", False),
        pytest.param(DCPRRequestStatus.AWAITING_CSI_REVIEW, "other", False),
        pytest.param(DCPRRequestStatus.UNDER_CSI_REVIEW, "owner", False),
        pytest.param(DCPRRequestStatus.UNDER_CSI_REVIEW, "anonymous", False),
        pytest.param(DCPRRequestStatus.UNDER_CSI_REVIEW, "other", False),
        pytest.param(DCPRRequestStatus.ACCEPTED, "owner", False),
        pytest.param(DCPRRequestStatus.ACCEPTED, "anonymous", False),
        pytest.param(DCPRRequestStatus.ACCEPTED, "other", False),
        pytest.param(DCPRRequestStatus.REJECTED, "owner", False),
        pytest.param(DCPRRequestStatus.REJECTED, "anonymous", False),
        pytest.param(DCPRRequestStatus.REJECTED, "other", False),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_submit_dcpr_request(target_status, actor, should_succeed):
    user = factories.User()
    organization = factories.Organization()
    _create_membership(user, organization)
    created = _get_dcpr_request(user, organization)
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    meta.Session.commit()
    action = toolkit.get_action("dcpr_request_submit")
    action_data_dict = {"csi_reference_id": created["csi_reference_id"]}
    action_context = {}
    if actor == "owner":
        action_context["user"] = user["name"]
    elif actor == "anonymous":
        pass
    elif actor == "other":
        another_user = factories.User()
        action_context["user"] = another_user["name"]
    else:
        raise NotImplementedError

    if should_succeed:
        action(context=action_context, data_dict=action_data_dict)
        updated = helpers.call_action(
            "dcpr_request_show",
            context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
            csi_reference_id=created["csi_reference_id"],
        )
        assert updated["status"] == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    else:
        with pytest.raises(toolkit.NotAuthorized):
            action(context=action_context, data_dict=action_data_dict)


@pytest.mark.parametrize(
    "claim_action, target_status, actor, should_succeed, reviewer_attribute, expect_reviewer",
    [
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "nsif_member",
            True,
            "nsif_reviewer",
            True,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "nsif_member",
            True,
            "nsif_reviewer",
            False,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_nsif_reviewer",
            DCPRRequestStatus.REJECTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "csi_member",
            True,
            "csi_moderator",
            True,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "claim_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_PREPARATION,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_NSIF_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.AWAITING_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "csi_member",
            True,
            "csi_moderator",
            False,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "nsif_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.UNDER_CSI_REVIEW,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.ACCEPTED,
            "other",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "csi_member",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "owner",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "anonymous",
            False,
            None,
            None,
        ),
        pytest.param(
            "resign_dcpr_request_csi_reviewer",
            DCPRRequestStatus.REJECTED,
            "other",
            False,
            None,
            None,
        ),
    ],
)
@pytest.mark.usefixtures("emc_clean_db", "with_plugins", "with_request_context")
def test_claim_nsif_dcpr_request(
    claim_action: str,
    target_status: DCPRRequestStatus,
    actor: str,
    should_succeed: bool,
    reviewer_attribute: str,
    expect_reviewer: bool,
):
    owner_user = factories.User()
    owner_org = factories.Organization()
    nsif_org = factories.Organization(name=NSIF_ORG_NAME)
    nsif_member = factories.User()
    _create_membership(nsif_member, nsif_org)
    csi_org = factories.Organization(name=CSI_ORG_NAME)
    csi_member = factories.User()
    _create_membership(csi_member, csi_org)
    created = _get_dcpr_request(owner_user, owner_org)
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    meta.Session.commit()
    action = toolkit.get_action(claim_action)
    action_data_dict = {"csi_reference_id": created["csi_reference_id"]}
    action_context = {}
    if actor == "nsif_member":
        action_context["user"] = nsif_member["name"]
    elif actor == "csi_member":
        action_context["user"] = csi_member["name"]
    elif actor == "owner":
        action_context["user"] = owner_user["name"]
    elif actor == "anonymous":
        pass
    elif actor == "other":
        another_user = factories.User()
        action_context["user"] = another_user["name"]
    else:
        raise NotImplementedError
    if should_succeed:
        action(context=action_context, data_dict=action_data_dict)
        updated = helpers.call_action(
            "dcpr_request_show",
            context={
                "user": owner_user["name"],
                "auth_user_obj": User.get(owner_user["id"]),
            },
            csi_reference_id=created["csi_reference_id"],
        )
        if expect_reviewer:
            assert updated[reviewer_attribute] == User.get(action_context["user"]).id
        else:
            assert updated[reviewer_attribute] is None
    else:
        with pytest.raises(toolkit.NotAuthorized):
            action(context=action_context, data_dict=action_data_dict)


# def test_moderate_dcpr_request_by_nsif():
#     # - moderating a request that has a status different then UNDER_NSIF_REVIEW fails
#     # - moderating a request by the nsif_reviewer works
#     # - moderating a request by the sysadmin works
#     # - moderating a request by a user that is not the nsif_reviewer fails
#     # - after moderation, the status changes to AWAITING_CSI_MODERATION if the moderation result was accepted
#     # - after moderation, the status changes to REJECTED if the moderation result was not accepted
#     raise NotImplementedError
#
#
# def test_moderate_dcpr_request_by_csi():
#     # - moderating a request that has a status different then UNDER_CSI_REVIEW fails
#     # - moderating a request by the csi_reviewer works
#     # - moderating a request by the sysadmin works
#     # - moderating a request by a user that is not the nsif_reviewer fails
#     # - after moderation, the status changes to either ACCEPTED or REJECTED, depending on the payload
#     raise NotImplementedError


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


def _get_dcpr_request(user, organization):
    return toolkit.get_action("dcpr_request_create")(
        context={"user": user["name"]},
        data_dict={
            "proposed_project_name": f"test",
            "capture_start_date": "2022-01-01",
            "capture_end_date": "2022-01-02",
            "cost": "200000",
            "organization_id": organization["id"],
            "datasets": [
                {
                    "proposed_dataset_title": "dummy",
                    "dataset_purpose": "dummy",
                }
            ],
        },
    )
