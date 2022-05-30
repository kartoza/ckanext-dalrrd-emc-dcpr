import uuid
import pytest
import logging

from ckan.tests import (
    factories,
    helpers,
)

from ckan.plugins import toolkit
from ckan import model, logic
from sqlalchemy import exc

from ckanext.dalrrd_emc_dcpr.cli._sample_dcpr_requests import (
    SAMPLE_REQUESTS,
    SAMPLE_GEOSPATIAL_REQUESTS,
)

from ckanext.dalrrd_emc_dcpr.model.dcpr_request import DCPRRequestStatus

logger = logging.getLogger(__name__)


pytestmark = pytest.mark.integration

REQUEST_TEST_DATA = {
    "status": "status",
    "organization_name": "organization_name",
    "organization_level": "organization_level",
    "organization_address": "organization_address",
    "proposed_project_name": "proposed_project_name",
    "additional_project_context": "additional_project_context",
    "capture_start_date": "2022-01-01",
    "capture_end_date": "2022-01-01",
    "cost": "cost",
    "spatial_extent": "spatial_extent",
    "spatial_resolution": "EPSG:4326",
    "data_capture_urgency": "data_capture_urgency",
    "additional_information": "additional_information",
    "dataset_custodian": True,
    "data_type": "data_type",
    "proposed_dataset_title": "proposed_dataset_title",
    "proposed_abstract": "proposed_abstract",
    "dataset_purpose": "dataset_purpose",
    "lineage_statement": "lineage_statement",
    "associated_attributes": "associated_attributes",
    "feature_description": "feature_description",
    "data_usage_restrictions": "data_usage_restrictions",
    "capture_method": "capture_method",
    "capture_method_detail": "capture_method_detail",
}


@pytest.mark.parametrize(
    "name, user_available, user_logged, test_schema_validation",
    [
        pytest.param(
            "request_1",
            True,
            True,
            False,
            id="request-added-successfully",
        ),
        pytest.param(
            "request_2",
            False,
            True,
            False,
            marks=pytest.mark.raises(exception=exc.IntegrityError),
            id="request-can-not-be-added-integrity-error",
        ),
        pytest.param(
            "request_3",
            True,
            True,
            False,
            id="request-can-be-added-custom-request-id",
        ),
        pytest.param(
            "request_2",
            False,
            True,
            True,
            marks=pytest.mark.raises(exception=toolkit.ValidationError),
            id="request-creation-returns-validation-error",
        ),
    ],
)
def test_create_dcpr_request(name, user_available, user_logged, test_schema_validation):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )

    data_dict = REQUEST_TEST_DATA
    data_dict["owner_user"] = user_id

    if test_schema_validation:
        data_dict["proposed_project_name"] = None

    context = {"ignore_auth": not user_logged, "user": user["name"]}

    dcpr_request = helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    assert dcpr_request.status == DCPRRequestStatus.UNDER_PREPARATION.value


@pytest.mark.parametrize(
    "name, user_available, user_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-created-and-updated-successfully",
        ),
        pytest.param(
            "request_2",
            True,
            False,
            id="request-update-exceptions",
            marks=pytest.mark.raises(exception=toolkit.NotAuthorized),
        ),
    ],
)
def test_update_dcpr_request(name, user_available, user_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )

    data_dict = REQUEST_TEST_DATA
    data_dict["owner_user"] = user_id
    data_dict["proposed_project_name"] = "proposed_project_name"

    context = {"ignore_auth": not user_logged, "user": user["name"]}

    dcpr_request_obj = helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    data_dict["request_id"] = dcpr_request_obj.csi_reference_id
    data_dict["proposed_project_name"] = "new_project_name"

    if not user_logged:
        context["auth_user_obj"] = None
        context["user"] = None
        context["ignore_auth"] = False

    logger.debug(f"dicts {context}")

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_update",
        context=context,
        **data_dict,
    )

    assert dcpr_request_updated_obj.status == dcpr_request_obj.status
    assert (
        dcpr_request_updated_obj.proposed_project_name
        != dcpr_request_obj.proposed_project_name
    )


@pytest.mark.parametrize(
    "name, user_available, owner_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-submitted-successfully",
        ),
        pytest.param(
            "request_2",
            True,
            False,
            id="request-submit-exceptions",
            marks=pytest.mark.raises(exception=toolkit.NotAuthorized),
        ),
    ],
)
def test_submit_dcpr_request(name, user_available, owner_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )
    data_dict = REQUEST_TEST_DATA
    data_dict["owner_user"] = user_id

    context = {"ignore_auth": not owner_logged, "user": user["name"]}

    helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    if not owner_logged:
        context["auth_user_obj"] = None
        context["user"] = None
        context["ignore_auth"] = False

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_submit",
        context=context,
        **data_dict,
    )

    assert (
        dcpr_request_updated_obj.status == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )


@pytest.mark.parametrize(
    "name, user_available, owner_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-submitted-successfully",
        ),
        pytest.param(
            "request_2",
            True,
            False,
            id="request-escalate-exceptions",
            marks=pytest.mark.raises(exception=toolkit.NotAuthorized),
        ),
    ],
)
def test_escalate_dcpr_request(name, user_available, owner_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )
    data_dict = REQUEST_TEST_DATA
    data_dict["owner_user"] = user_id

    context = {"ignore_auth": not owner_logged, "user": user["name"]}

    helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    helpers.call_action(
        "dcpr_request_submit",
        context=context,
        **data_dict,
    )

    if not owner_logged:
        context["auth_user_obj"] = None
        context["user"] = None
        context["ignore_auth"] = False

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_escalate",
        context=context,
        **data_dict,
    )

    assert (
        dcpr_request_updated_obj.status == DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )


@pytest.mark.parametrize(
    "name, user_available, owner_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-submitted-successfully",
        ),
        pytest.param(
            "request_2",
            True,
            False,
            id="request-accept-exceptions",
            marks=pytest.mark.raises(exception=toolkit.NotAuthorized),
        ),
    ],
)
def test_accept_dcpr_request(name, user_available, owner_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )
    data_dict = REQUEST_TEST_DATA
    data_dict["owner_user"] = user_id

    context = {
        "ignore_auth": not owner_logged,
        "user": user["name"],
        "auth_user_obj": model.User(id=user.get("id")),
    }

    helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    helpers.call_action(
        "dcpr_request_submit",
        context=context,
        **data_dict,
    )

    helpers.call_action(
        "dcpr_request_escalate",
        context=context,
        **data_dict,
    )

    if not owner_logged:
        context["auth_user_obj"] = None
        context["user"] = None
        context["ignore_auth"] = False

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_accept",
        context=context,
        **data_dict,
    )

    assert dcpr_request_updated_obj.status == DCPRRequestStatus.ACCEPTED.value


@pytest.mark.parametrize(
    "name, user_available, owner_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-submitted-successfully",
        ),
        pytest.param(
            "request_2",
            True,
            False,
            id="request-reject-exceptions",
            marks=pytest.mark.raises(exception=toolkit.NotAuthorized),
        ),
    ],
)
def test_reject_dcpr_request(name, user_available, owner_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )
    data_dict = REQUEST_TEST_DATA
    data_dict["owner_user"] = user_id

    context = {
        "ignore_auth": not owner_logged,
        "user": user["name"],
        "auth_user_obj": model.User(id=user.get("id")),
    }

    helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    helpers.call_action(
        "dcpr_request_submit",
        context=context,
        **data_dict,
    )

    helpers.call_action(
        "dcpr_request_escalate",
        context=context,
        **data_dict,
    )

    csi_reviewers = toolkit.h["emc_org_member_list"]("csi", role="editor")
    csi_user = toolkit.get_action("user_show")(
        {"ignore_auth": True}, {"id": csi_reviewers[0]}
    )
    user = model.User(id=csi_user.get("id"), name=csi_user.get("name"))

    context["auth_user_obj"] = user
    context["user"] = csi_user.get("name")

    if not owner_logged:
        context["auth_user_obj"] = None
        context["user"] = None
        context["ignore_auth"] = False

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_reject",
        context=context,
        **data_dict,
    )

    assert dcpr_request_updated_obj.status == DCPRRequestStatus.REJECTED.value


@pytest.mark.parametrize(
    "request_id, name, user_available, user_logged",
    [
        pytest.param(
            uuid.uuid4(),
            "request_1",
            True,
            True,
            id="request-added-successfully",
        ),
        pytest.param(
            uuid.uuid4(),
            "request_2",
            False,
            True,
            marks=pytest.mark.raises(exception=exc.IntegrityError),
            id="request-can-not-be-added-integrity-error",
        ),
        pytest.param(
            uuid.uuid4(),
            "request_3",
            True,
            True,
            id="request-can-be-added-custom-request-id",
        ),
    ],
)
def test_create_dcpr_geospatial_request(request_id, name, user_available, user_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )

    for request in SAMPLE_GEOSPATIAL_REQUESTS:
        data_dict = {
            "csi_reference_id": request_id,
            "owner_user": user_id,
            "csi_reviewer": user_id,
            "nsif_reviewer": user_id,
            "notification_targets": [{"user_id": user_id, "group_id": None}],
            "status": request.status,
            "organization_name": request.organization_name,
            "dataset_purpose": request.dataset_purpose,
            "interest_region": request.interest_region,
            "resolution_scale": request.resolution_scale,
            "additional_information": request.additional_information,
            "request_date": request.request_date,
            "submission_date": request.submission_date,
            "nsif_review_date": request.nsif_review_date,
            "nsif_review_notes": request.nsif_review_notes,
            "nsif_review_additional_documents": request.nsif_review_additional_documents,
            "csi_moderation_notes": request.csi_moderation_notes,
            "csi_review_additional_documents": request.csi_review_additional_documents,
            "csi_moderation_date": request.csi_moderation_date,
            "dataset_sasdi_category": request.dataset_sasdi_category,
            "custodian_organization": request.custodian_organization,
            "data_type": request.data_type,
        }

        context = {"ignore_auth": not user_logged, "user": user["name"]}

        helpers.call_action(
            "dcpr_geospatial_request_create",
            context=context,
            **data_dict,
        )
