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

    for request in SAMPLE_REQUESTS:
        data_dict = {
            "owner_user": user_id,
            "organization_name": request.organization_name,
            "organization_level": request.organization_level,
            "organization_address": request.organization_address,
            "additional_project_context": request.additional_project_context,
            "capture_start_date": request.capture_start_date,
            "capture_end_date": request.capture_end_date,
            "cost": request.cost,
            "spatial_extent": request.spatial_extent,
            "spatial_resolution": request.spatial_resolution,
            "data_capture_urgency": request.data_capture_urgency,
            "additional_information": request.additional_information,
            "dataset_custodian": request.dataset_custodian,
            "data_type": request.data_type,
            "proposed_dataset_title": request.proposed_dataset_title,
            "proposed_abstract": request.proposed_abstract,
            "dataset_purpose": request.dataset_purpose,
            "lineage_statement": request.lineage_statement,
            "associated_attributes": request.associated_attributes,
            "feature_description": request.feature_description,
            "data_usage_restrictions": request.data_usage_restrictions,
            "capture_method": request.capture_method,
            "capture_method_detail": request.capture_method_detail,
            "action_type": 0,
        }

        if not test_schema_validation:
            data_dict["proposed_project_name"] = request.proposed_project_name

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
    dcpr_request = SAMPLE_REQUESTS[0]

    data_dict = {
        "owner_user": user_id,
        "organization_name": dcpr_request.organization_name,
        "organization_level": dcpr_request.organization_level,
        "organization_address": dcpr_request.organization_address,
        "proposed_project_name": dcpr_request.proposed_project_name,
        "additional_project_context": dcpr_request.additional_project_context,
        "capture_start_date": dcpr_request.capture_start_date,
        "capture_end_date": dcpr_request.capture_end_date,
        "cost": dcpr_request.cost,
        "spatial_extent": dcpr_request.spatial_extent,
        "spatial_resolution": dcpr_request.spatial_resolution,
        "data_capture_urgency": dcpr_request.data_capture_urgency,
        "additional_information": dcpr_request.additional_information,
        "dataset_custodian": dcpr_request.dataset_custodian,
        "data_type": dcpr_request.data_type,
        "proposed_dataset_title": dcpr_request.proposed_dataset_title,
        "proposed_abstract": dcpr_request.proposed_abstract,
        "dataset_purpose": dcpr_request.dataset_purpose,
        "lineage_statement": dcpr_request.lineage_statement,
        "associated_attributes": dcpr_request.associated_attributes,
        "feature_description": dcpr_request.feature_description,
        "data_usage_restrictions": dcpr_request.data_usage_restrictions,
        "capture_method": dcpr_request.capture_method,
        "capture_method_detail": dcpr_request.capture_method_detail,
        "action_type": 0,
    }

    context = {"ignore_auth": not user_logged, "user": user["name"]}

    dcpr_request_obj = helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    data_dict["action_type"] = 1
    data_dict["request_id"] = dcpr_request_obj.csi_reference_id

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_update",
        context=context,
        **data_dict,
    )

    assert (
        dcpr_request_updated_obj.status == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )

    nsif_reviewers = toolkit.h["emc_org_member_list"]("nsif", role="editor")
    nsif_user = toolkit.get_action("user_show")(
        {"ignore_auth": True}, {"id": nsif_reviewers[0]}
    )

    user = model.User(id=nsif_user.get("id"), name=nsif_user.get("name"))

    data_dict["action_type"] = 4
    data_dict["request_id"] = dcpr_request_obj.csi_reference_id

    context["auth_user_obj"] = user
    context["user"] = nsif_user.get("name")

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_update",
        context=context,
        **data_dict,
    )

    assert (
        dcpr_request_updated_obj.status == DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )

    csi_reviewers = toolkit.h["emc_org_member_list"]("csi", role="editor")
    csi_user = toolkit.get_action("user_show")(
        {"ignore_auth": True}, {"id": csi_reviewers[0]}
    )
    user = model.User(id=csi_user.get("id"), name=csi_user.get("name"))

    context["auth_user_obj"] = user
    context["user"] = csi_user.get("name")

    data_dict["action_type"] = 2

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_update",
        context=context,
        **data_dict,
    )

    assert dcpr_request_updated_obj.status == DCPRRequestStatus.ACCEPTED.value


@pytest.mark.parametrize(
    "name, user_available, user_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-update-exceptions",
            marks=pytest.mark.raises(exception=toolkit.NotAuthorized),
        ),
    ],
)
def test_update_dcpr_request_exceptions(name, user_available, user_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )
    dcpr_request = SAMPLE_REQUESTS[0]

    data_dict = {
        "owner_user": user_id,
        "organization_name": dcpr_request.organization_name,
        "organization_level": dcpr_request.organization_level,
        "organization_address": dcpr_request.organization_address,
        "proposed_project_name": dcpr_request.proposed_project_name,
        "additional_project_context": dcpr_request.additional_project_context,
        "capture_start_date": dcpr_request.capture_start_date,
        "capture_end_date": dcpr_request.capture_end_date,
        "cost": dcpr_request.cost,
        "spatial_extent": dcpr_request.spatial_extent,
        "spatial_resolution": dcpr_request.spatial_resolution,
        "data_capture_urgency": dcpr_request.data_capture_urgency,
        "additional_information": dcpr_request.additional_information,
        "dataset_custodian": dcpr_request.dataset_custodian,
        "data_type": dcpr_request.data_type,
        "proposed_dataset_title": dcpr_request.proposed_dataset_title,
        "proposed_abstract": dcpr_request.proposed_abstract,
        "dataset_purpose": dcpr_request.dataset_purpose,
        "lineage_statement": dcpr_request.lineage_statement,
        "associated_attributes": dcpr_request.associated_attributes,
        "feature_description": dcpr_request.feature_description,
        "data_usage_restrictions": dcpr_request.data_usage_restrictions,
        "capture_method": dcpr_request.capture_method,
        "capture_method_detail": dcpr_request.capture_method_detail,
        "action_type": 0,
    }

    context = {"ignore_auth": not user_logged, "user": user["name"]}

    dcpr_request_obj = helpers.call_action(
        "dcpr_request_create",
        context=context,
        **data_dict,
    )

    data_dict["action_type"] = 1
    data_dict["request_id"] = dcpr_request_obj.csi_reference_id

    dcpr_request_updated_obj = helpers.call_action(
        "dcpr_request_update",
        context=context,
        **data_dict,
    )

    assert (
        dcpr_request_updated_obj.status == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )

    nsif_reviewers = toolkit.h["emc_org_member_list"]("nsif", role="editor")
    nsif_user = toolkit.get_action("user_show")(
        {"ignore_auth": True}, {"id": nsif_reviewers[0]}
    )

    user = model.User(id=nsif_user.get("id"), name=nsif_user.get("name"))

    data_dict["action_type"] = 2
    data_dict["request_id"] = dcpr_request_obj.csi_reference_id

    context["auth_user_obj"] = user
    context["user"] = nsif_user.get("name")

    helpers.call_action(
        "dcpr_request_update",
        context=context,
        **data_dict,
    )


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
