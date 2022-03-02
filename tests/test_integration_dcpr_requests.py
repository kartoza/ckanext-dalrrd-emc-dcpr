import json
import pytest

from ckan.tests import (
    factories,
    helpers,
)

from ckan.plugins import toolkit
from ckan import model

from ckanext.dalrrd_emc_dcpr.cli._sample_dcpr_requests import SAMPLE_REQUESTS

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            "request_1",
            id="request-added-successfully",
        ),
    ],
)
def test_create_dcpr_request(name):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = convert_user_name_or_id_to_id(user["name"], {"session": model.Session})

    for request in SAMPLE_REQUESTS:
        data_dict = {
            "csi_reference_id": request.csi_reference_id,
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
            "request_dataset": request.request_dataset,
            "cost": request.cost,
            "spatial_extent": request.spatial_extent,
            "spatial_resolution": request.spatial_resolution,
            "data_capture_urgency": request.data_capture_urgency,
            "additional_information": request.additional_information,
            "request_date": request.request_date,
            "submission_date": request.submission_date,
        }

        helpers.call_action(
            "dcpr_request_create",
            context={"ignore_auth": False, "user": user["name"]},
            **data_dict,
        )
