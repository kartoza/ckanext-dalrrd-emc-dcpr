import logging
import typing

import ckan.plugins.toolkit as toolkit

from sqlalchemy import select, exc

# from ckanext.dalrrd_emc_dcpr.model.request import DCPRRequest
from ...model import dcpr_request as dcpr_request

logger = logging.getLogger(__name__)


def dcpr_request_create(context, data_dict):
    model = context["model"]
    access = toolkit.check_access("dcpr_request_create_auth", context, data_dict)
    logger.debug("Inside the dcpr_request_create action")

    if not access:
        raise toolkit.NotAuthorized({"message": "Unauthorized to perform action"})

    csi_reference_id = str(data_dict["csi_reference_id"])
    request = dcpr_request.DCPRRequest.get(csi_reference_id=csi_reference_id)

    if request:
        raise toolkit.ValidationError({"message": "DCPR request already exists"})
    else:
        request = dcpr_request.DCPRRequest(
            csi_reference_id=data_dict["csi_reference_id"],
            owner_user=data_dict["owner_user"],
            csi_moderator=data_dict["csi_moderator"],
            nsif_reviewer=data_dict["nsif_reviewer"],
            status=data_dict["status"],
            organization_name=data_dict["organization_name"],
            organization_level=data_dict["organization_level"],
            organization_address=data_dict["organization_address"],
            proposed_project_name=data_dict["proposed_project_name"],
            additional_project_context=data_dict["additional_project_context"],
            capture_start_date=data_dict["capture_start_date"],
            capture_end_date=data_dict["capture_end_date"],
            cost=data_dict["cost"],
            spatial_extent=data_dict["spatial_extent"],
            spatial_resolution=data_dict["spatial_resolution"],
            data_capture_urgency=data_dict["data_capture_urgency"],
            additional_information=data_dict["additional_information"],
            request_date=data_dict["request_date"],
            submission_date=data_dict["submission_date"],
            nsif_review_date=data_dict["nsif_review_date"],
            nsif_recommendation=data_dict["nsif_recommendation"],
            nsif_review_notes=data_dict["nsif_review_notes"],
            nsif_review_additional_documents=data_dict[
                "nsif_review_additional_documents"
            ],
            csi_moderation_notes=data_dict["csi_moderation_notes"],
            csi_moderation_additional_documents=data_dict[
                "csi_moderation_additional_documents"
            ],
            csi_moderation_date=data_dict["csi_moderation_date"],
        )

        request_dataset = dcpr_request.DCPRRequestDataset(
            dcpr_request_id=data_dict["csi_reference_id"],
            dataset_custodian=data_dict["dataset_custodian"],
            data_type=data_dict["data_type"],
            purposed_dataset_title=data_dict["purposed_dataset_title"],
            purposed_abstract=data_dict["purposed_abstract"],
            dataset_purpose=data_dict["dataset_purpose"],
            lineage_statement=data_dict["lineage_statement"],
            associated_attributes=data_dict["associated_attributes"],
            feature_description=data_dict["feature_description"],
            data_usage_restrictions=data_dict["data_usage_restrictions"],
            capture_method=data_dict["capture_method"],
            capture_method_detail=data_dict["capture_method_detail"],
        )
        notification_targets = []

        for target in data_dict["notification_targets"]:
            target = dcpr_request.DCPRRequestNotificationTarget(
                dcpr_request_id=data_dict["csi_reference_id"],
                user_id=target.get("user_id"),
                group_id=target.get("group_id"),
            )
            notification_targets.append(target)

    try:
        model.Session.add(request)
        model.repo.commit()
        model.Session.add(request_dataset)

        model.Session.add_all(notification_targets)

        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return request


def dcpr_geospatial_request_create(context, data_dict):
    model = context["model"]
    access = toolkit.check_access("dcpr_request_create_auth", context, data_dict)
    logger.debug("Inside the dcpr_request_create action")

    if not access:
        raise toolkit.NotAuthorized({"message": "Unauthorized to perform action"})

    csi_reference_id = str(data_dict["csi_reference_id"])
    request = dcpr_request.DCPRGeospatialRequest.get(csi_reference_id=csi_reference_id)

    if request:
        raise toolkit.ValidationError(
            {"message": "DCPR geospatial request already exists"}
        )
    else:
        request = dcpr_request.DCPRGeospatialRequest(
            csi_reference_id=data_dict["csi_reference_id"],
            owner_user=data_dict["owner_user"],
            csi_reviewer=data_dict["csi_reviewer"],
            nsif_reviewer=data_dict["nsif_reviewer"],
            status=data_dict["status"],
            organization_name=data_dict["organization_name"],
            dataset_purpose=data_dict["dataset_purpose"],
            interest_region=data_dict["interest_region"],
            resolution_scale=data_dict["resolution_scale"],
            additional_information=data_dict["additional_information"],
            request_date=data_dict["request_date"],
            submission_date=data_dict["submission_date"],
            nsif_review_date=data_dict["nsif_review_date"],
            nsif_review_notes=data_dict["nsif_review_notes"],
            nsif_review_additional_documents=data_dict[
                "nsif_review_additional_documents"
            ],
            csi_moderation_notes=data_dict["csi_moderation_notes"],
            csi_review_additional_documents=data_dict[
                "csi_review_additional_documents"
            ],
            csi_moderation_date=data_dict["csi_moderation_date"],
            dataset_sasdi_category=data_dict["dataset_sasdi_category"],
            custodian_organization=data_dict["custodian_organization"],
            data_type=data_dict["data_type"],
        )
        notification_targets = []

        for target in data_dict["notification_targets"]:
            target = dcpr_request.DCPRGeospatialRequestNotificationTarget(
                dcpr_request_id=data_dict["csi_reference_id"],
                user_id=target.get("user_id"),
                group_id=target.get("group_id"),
            )
            notification_targets.append(target)

    try:
        model.Session.add(request)
        model.repo.commit()
        model.Session.add_all(notification_targets)
        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return request


@toolkit.side_effect_free
def dcpr_request_list(context: typing.Dict, data_dict: typing.Dict) -> typing.List:
    """Present relevant DCPR requests to user

    Anonymous users are able to view all moderated requests

    Unmoderated requests are available only to:
    - the creator
    - a sysadmin
    - if the request has been submitted to users of the current workflow stage

    """

    logger.debug("Inside the dcpr_request_list action")
    access_result = toolkit.check_access(
        "dcpr_request_list_auth", context, data_dict=data_dict
    )
    logger.debug(f"access_result: {access_result}")
    user = context["auth_user_obj"]
    model = context["model"]
    request_table = dcpr_request.dcpr_request_table
    query = select([request_table.c.csi_reference_id])
    if user is None:  # show only  moderated requests
        pass
    elif user.sysadmin:  # show all requests
        pass
    else:  # show relevant requests depending on the user's organization
        pass
    query = query.order_by(request_table.c.csi_reference_id)
    limit = data_dict.get("limit", 10)
    offset = data_dict.get("offset", 10)
    query = query.limit(limit).offset(offset)
    return [r[0] for r in query.execute()]
