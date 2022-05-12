import pytest

from ckan.model import User, meta
from ckan.plugins import toolkit
from ckan.tests import factories, helpers

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
    helpers.call_action(
        "organization_member_create",
        id=organization["id"],
        username=user["name"],
        role="member",
    )
    dcpr_request_data_dict["organization_id"] = organization["id"]
    print(f"{dcpr_request_data_dict=}")
    created = helpers.call_action(
        "dcpr_request_create",
        context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
        **dcpr_request_data_dict,
    )
    print(f"{created=}")
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    print(f"{request_obj=}")
    meta.Session.commit()
    public_records = helpers.call_action("dcpr_request_list_public")
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
    helpers.call_action(
        "organization_member_create",
        id=organization["id"],
        username=user["name"],
        role="member",
    )
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
    created = helpers.call_action(
        "dcpr_request_create",
        context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
        **dcpr_request_data_dict,
    )
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    print(f"{request_obj=}")
    meta.Session.commit()
    my_requests = helpers.call_action(
        "my_dcpr_request_list",
        context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
    )
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
        helpers.call_action(
            "organization_member_create",
            id=organization["id"],
            username=user["name"],
            role="member",
        )
        context = {"user": user["name"], "auth_user_obj": User.get(user["id"])}
    elif is_sysadmin:
        user = factories.User(sysadmin=True)
        context = {"user": user["name"], "auth_user_obj": User.get(user["id"])}
    else:
        user = factories.User()
        context = {"user": user["name"], "auth_user_obj": User.get(user["id"])}
    helpers.call_action(
        "dcpr_request_create", context=context, **dcpr_request_data_dict
    )


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
def test_delete_dcpr_request(target_status):
    # - deletion of a request by the owner works
    # - deletion of a request by the admin works
    # - deletion of a request by any other user fails
    # - deletion of a request when its status is different from UNDER_PREPARATION fails
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
    user = factories.User()
    helpers.call_action(
        "organization_member_create",
        id=organization["id"],
        username=user["name"],
        role="member",
    )
    created = helpers.call_action(
        "dcpr_request_create",
        context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
        **dcpr_request_data_dict,
    )
    print(f"{created=}")
    request_obj = dcpr_request.DCPRRequest.get(created["csi_reference_id"])
    request_obj.status = target_status.value
    meta.Session.commit()
    delete_result = helpers.call_action(
        "dcpr_request_delete",
        context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
        csi_reference_id=created["csi_reference_id"],
    )
    print(f"{delete_result=}")
    # FIXME: this assertion is not right
    with pytest.raises(toolkit.ObjectNotFound):
        show_result = helpers.call_action(
            "dcpr_request_show",
            context={"user": user["name"], "auth_user_obj": User.get(user["id"])},
            csi_reference_id=created["csi_reference_id"],
        )
        print(f"{show_result=}")


def test_update_dcpr_request_by_owner():
    # - updating an existing request that has a different status than UNDER_PREPARATION fails
    # - updating user-related fields works
    # - updating other fields than the user-related ones fails
    # - updating an existing request by a user that is not its owner fails
    # - updating an existing request by the owner works
    # - modifying a request's status manually does not work
    # - updating an existing request by an admin works
    raise NotImplementedError


def test_submit_dcpr_request():
    # - submitting a request works when done by its owner
    # - submitting a request does not work for anonymous users
    # - submitting a request does not work for logged in users
    # - submitting a request does not work for members of NSIF org
    # - submitting a request does not work for members of CSI org
    raise NotImplementedError


def test_claim_nsif_dcpr_request():
    # - claiming a request on behalf of NSIF when the request status is not AWAITING_NSIF_REVIEW does not work
    # - claiming a request on behalf of NSIF works when done by an NSIF member
    # - claiming a request on behalf of NSIF does not work when done by a non-NSIF member
    raise NotImplementedError


def test_resign_nsif_reviewer_dcpr_request():
    # - resigning from the role of NSIF reviewer when the request status is not UNDER_NSIF_REVIEW does not work
    # - resigning from the role of NSIF reviewer works when the user is the current reviewer
    # - resigning from the role of NSIF reviewer works when the user is a sysadmin
    # - resigning from the role of NSIF reviewer does not work when the user is not the current reviewer
    raise NotImplementedError


def test_claim_csi_dcpr_request():
    # - claiming a request on behalf of CSI when the request status is not AWAITING_CSI_REVIEW does not work
    # - claiming a request on behalf of CSI works when done by an CSI member
    # - claiming a request on behalf of CSI does not work when done by a non-CSI member
    raise NotImplementedError


def test_resign_csi_reviewer_dcpr_request():
    # - resigning from the role of CSI reviewer when the request status is not UNDER_CSI_REVIEW does not work
    # - resigning from the role of CSI reviewer works when the user is the current reviewer
    # - resigning from the role of CSI reviewer works when the user is a sysadmin
    # - resigning from the role of CSI reviewer does not work when the user is not the current reviewer
    raise NotImplementedError


def test_update_dcpr_request_by_nsif():
    # - updating an existing request that has a different status than UNDER_NSIF_REVIEW fails
    # - updating nsif-related fields works
    # - updating other fields fails
    # - updating an existing request by a user that is not its nsif_reviewer fails
    # - updating an existing request by a user that has no nsif_reviewer fails
    # - updating an existing request by an admin works
    raise NotImplementedError


def test_update_dcpr_request_by_csi():
    # - updating an existing request that has a different status than UNDER_CSI_REVIEW fails
    # - updating csi-related fields works
    # - updating other fields fails
    # - updating an existing request by a user that is not its csi_reviewer fails
    # - updating an existing request that has no csi_reviewer fails
    # - updating an existing request by an admin works
    raise NotImplementedError


def test_moderate_dcpr_request_by_nsif():
    # - moderating a request that has a status different then UNDER_NSIF_REVIEW fails
    # - moderating a request by the nsif_reviewer works
    # - moderating a request by the sysadmin works
    # - moderating a request by a user that is not the nsif_reviewer fails
    # - after moderation, the status changes to AWAITING_CSI_MODERATION if the moderation result was accepted
    # - after moderation, the status changes to REJECTED if the moderation result was not accepted
    raise NotImplementedError


def test_moderate_dcpr_request_by_csi():
    # - moderating a request that has a status different then UNDER_CSI_REVIEW fails
    # - moderating a request by the csi_reviewer works
    # - moderating a request by the sysadmin works
    # - moderating a request by a user that is not the nsif_reviewer fails
    # - after moderation, the status changes to either ACCEPTED or REJECTED, depending on the payload
    raise NotImplementedError
