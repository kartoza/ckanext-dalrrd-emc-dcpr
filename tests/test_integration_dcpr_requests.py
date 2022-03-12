import uuid
import pytest

from ckan.tests import (
    factories,
    helpers,
)

from ckan.plugins import toolkit
from ckan import model, logic
from sqlalchemy import exc

from ckanext.dalrrd_emc_dcpr.cli._sample_dcpr_requests import SAMPLE_REQUESTS

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "name, user_available, user_logged",
    [
        pytest.param(
            "request_1",
            True,
            True,
            id="request-added-successfully",
        ),
        pytest.param(
            "request_2",
            False,
            True,
            marks=pytest.mark.raises(exception=exc.IntegrityError),
            id="request-can-not-be-added-integrity-error",
        ),
        pytest.param(
            "request_3",
            True,
            True,
            id="request-can-be-added-custom-request-id",
        ),
    ],
)
def test_create_dcpr_request(name, user_available, user_logged):
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
            "csi_reference_id": uuid.uuid4(),
            "owner_user": user_id,
            "csi_moderator": user_id,
            "nsif_reviewer": user_id,
            "notification_targets": [{"user_id": user_id, "group_id": None}],
            "status": request.status,
            "organization_name": request.organization_name,
            "organization_level": request.organization_level,
            "organization_address": request.organization_address,
            "proposed_project_name": request.proposed_project_name,
            "additional_project_context": request.additional_project_context,
            "capture_start_date": request.capture_start_date,
            "capture_end_date": request.capture_end_date,
            "cost": request.cost,
            "spatial_extent": request.spatial_extent,
            "spatial_resolution": request.spatial_resolution,
            "data_capture_urgency": request.data_capture_urgency,
            "additional_information": request.additional_information,
            "request_date": request.request_date,
            "submission_date": request.submission_date,
            "nsif_review_date": request.nsif_review_date,
            "nsif_recommendation": request.nsif_recommendation,
            "nsif_review_notes": request.nsif_review_notes,
            "nsif_review_additional_documents": request.nsif_review_additional_documents,
            "csi_moderation_notes": request.csi_moderation_notes,
            "csi_moderation_additional_documents": request.csi_moderation_additional_documents,
            "csi_moderation_date": request.csi_moderation_date,
            "dataset_custodian": request.dataset_custodian,
            "data_type": request.data_type,
            "purposed_dataset_title": request.purposed_dataset_title,
            "purposed_abstract": request.purposed_abstract,
            "dataset_purpose": request.dataset_purpose,
            "lineage_statement": request.lineage_statement,
            "associated_attributes": request.associated_attributes,
            "feature_description": request.feature_description,
            "data_usage_restrictions": request.data_usage_restrictions,
            "capture_method": request.capture_method,
            "capture_method_detail": request.capture_method_detail,
        }

        context = {"ignore_auth": not user_logged, "user": user["name"]}

        helpers.call_action(
            "dcpr_request_create",
            context=context,
            **data_dict,
        )
