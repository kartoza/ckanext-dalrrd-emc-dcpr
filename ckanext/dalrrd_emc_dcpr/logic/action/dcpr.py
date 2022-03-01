import logging
import typing

import ckan.plugins.toolkit as toolkit

from ckanext.dalrrd_emc_dcpr.model.request import Request

logger = logging.getLogger(__name__)


def dcpr_request_create(context, data_dict):
    model = context["model"]
    user = context["user"]

    convert_user_name_or_id_to_id = toolkit.get_converter(
        'convert_user_name_or_id_to_id')
    user_id = convert_user_name_or_id_to_id(user, context)

    access = toolkit.check_access("dcpr_request_create_auth", context, data_dict)

    if not access:
        raise toolkit.NotAuthorized({"message": "Unauthorized to perform action"})
        return

    csi_reference_id = str(data_dict["csi_reference_id"])
    request = Request.custom_get(csi_reference_id=csi_reference_id)

    if request:
        raise toolkit.ValidationError({"message": "Request already exists"})
    else:
        request = Request(
            csi_reference_id=data_dict['csi_reference_id'],
            owner_user=user_id,
            csi_moderator=user_id,
            nsif_reviewer=user_id,
            status=data_dict['status'],
            organization_name=data_dict['organization_name'],
            organization_level=data_dict['organization_level'],
            organization_address=data_dict['organization_address'],
            proposed_project_name=data_dict['proposed_project_name'],
            additional_project_context=data_dict['additional_project_context'],
            capture_start_date=data_dict['capture_start_date'],
            capture_end_date=data_dict['capture_end_date'],
            request_dataset=data_dict['request_dataset'],
            cost=data_dict['cost'],
            spatial_extent="spatial_extent",
            spatial_resolution=data_dict['spatial_resolution'],
            data_capture_urgency=data_dict['data_capture_urgency'],
            additional_information=data_dict['additional_information'],
            request_date=data_dict['request_date'],
            submission_date=data_dict['submission_date'],
        )

    model.Session.add(request)
    model.repo.commit()

    return request


@toolkit.side_effect_free
def dcpr_request_list(context: typing.Dict, data_dict: typing.Dict) -> typing.List:
    logger.debug("Inside the dcpr_request_list action")
    access_result = toolkit.check_access(
        "dcpr_request_list_auth", context, data_dict=data_dict
    )
    logger.debug(f"access_result: {access_result}")
    fake_requests = [
        {"name": "req1", "owner": "tester1"},
        {"name": "req2", "owner": "tester1"},
        {"name": "req3", "owner": "tester1"},
        {"name": "req4", "owner": "tester2"},
    ]
    result = []
    current_user = context["auth_user_obj"]
    for dcpr_request in fake_requests:
        if dcpr_request["owner"] == current_user.name:
            result.append(dcpr_request)
    return result
