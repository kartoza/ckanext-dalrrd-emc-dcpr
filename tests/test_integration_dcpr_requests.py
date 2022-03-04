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
            uuid.UUID("1d2b018d-3e0b-479c-938c-582376f3cd4a"),
            "request_3",
            True,
            True,
            id="request-can-be-added-custom-request-id",
        ),
        pytest.param(
            uuid.UUID("1d2b018d-3e0b-479c-938c-582376f3cd4a"),
            "request_4",
            True,
            True,
            marks=pytest.mark.raises(exception=logic.ValidationError),
            id="request-can-not-be-added-validation-error",
        ),
    ],
)
def test_create_dcpr_request(request_id, name, user_available, user_logged):
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
            "csi_reference_id": request_id,
            "owner_user": user_id,
            "csi_moderator": user_id,
            "nsif_reviewer": user_id,
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
        }

        context = {"ignore_auth": not user_logged, "user": user["name"]}

        helpers.call_action(
            "dcpr_request_create",
            context=context,
            **data_dict,
        )
