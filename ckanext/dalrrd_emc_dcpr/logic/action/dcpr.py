import enum
import logging
import typing

from datetime import datetime

import ckan.plugins.toolkit as toolkit
from ckan.lib import search, plugins
import ckan.lib.dictization as d

from sqlalchemy import sql, select, exc

# from ckanext.dalrrd_emc_dcpr.model.request import DCPRRequest
from ...model import dcpr_request as dcpr_request
from ...model import dcpr_error_report

from ..schema import create_dcpr_request_schema, update_dcpr_request_schema

logger = logging.getLogger(__name__)


class DCPRRequestActionType(enum.Enum):
    SAVE = 0
    SUBMIT = 1
    ACCEPT = 2
    REJECT = 3
    ESCALATE_TO_CSI = 4


def dcpr_error_report_create(context, data_dict):
    toolkit.check_access("dcpr_error_report_create_auth", context, data_dict)
    logger.debug("Inside the dcpr_error_report_create action")

    csi_reference_id = str(data_dict["csi_reference_id"])
    report = dcpr_error_report.DCPRErrorReport.get(csi_reference_id=csi_reference_id)

    if report:
        raise toolkit.ValidationError(
            {"message": "The DCPR Error report already exists"}
        )
    else:
        report = dcpr_error_report.DCPRErrorReport(
            csi_reference_id=data_dict["csi_reference_id"],
            owner_user=data_dict["owner_user"],
            csi_reviewer=data_dict["csi_reviewer"],
            metadata_record=data_dict["metadata_record"],
            status=data_dict["status"],
            error_application=data_dict["error_application"],
            error_description=data_dict["error_description"],
            solution_description=data_dict["solution_description"],
            request_date=data_dict["request_date"],
            csi_review_additional_documents=data_dict[
                "csi_review_additional_documents"
            ],
            csi_moderation_notes=data_dict["csi_moderation_notes"],
            csi_moderation_date=data_dict["csi_moderation_date"],
        )

        notification_targets = []

        for target in data_dict["notification_targets"]:
            target = dcpr_error_report.DCPRErrorReportNotificationTarget(
                dcpr_error_report_id=data_dict["csi_reference_id"],
                user_id=target.get("user_id"),
                group_id=target.get("group_id"),
            )
            notification_targets.append(target)

    model = context["model"]
    try:
        model.Session.add(report)
        model.repo.commit()
        model.Session.add_all(notification_targets)
        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return report


def dcpr_request_create(context, data_dict):
    model = context["model"]
    access = toolkit.check_access("dcpr_request_create_auth", context, data_dict)

    logger.debug("Inside the dcpr_request_create action")

    if not access:
        raise toolkit.NotAuthorized({"message": "Unauthorized to perform action"})

    action_type = data_dict.get("action_type", None)
    action_type = int(action_type) if action_type is not None else None

    if action_type == DCPRRequestActionType.SAVE.value:
        status = dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    elif action_type == DCPRRequestActionType.SUBMIT.value:
        status = dcpr_request.DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
        data_dict["submission_date"] = datetime.now()
    else:
        raise NotImplementedError

    schema = context.get("schema", create_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    request = dcpr_request.DCPRRequest(
        owner_user=data_dict["owner_user"],
        csi_moderator=data_dict.get("csi_moderator", None),
        nsif_reviewer=data_dict.get("nsif_reviewer", None),
        status=status,
        organization_name=data_dict["organization_name"],
        organization_level=data_dict["organization_level"],
        organization_address=data_dict["organization_address"],
        proposed_project_name=data_dict["proposed_project_name"],
        additional_project_context=data_dict["additional_project_context"],
        capture_start_date=data_dict["capture_start_date"],
        capture_end_date=data_dict["capture_end_date"],
        cost=data_dict["cost"],
        spatial_extent=data_dict.get("spatial_extent", None),
        spatial_resolution=data_dict["spatial_resolution"],
        data_capture_urgency=data_dict.get("data_capture_urgency", None),
        additional_information=data_dict["additional_information"],
        request_date=data_dict.get("request_date", None),
        submission_date=data_dict.get("submission_date", None),
    )

    request_dataset = dcpr_request.DCPRRequestDataset(
        dataset_custodian=data_dict.get("dataset_custodian", False),
        data_type=data_dict["data_type"],
        proposed_dataset_title=data_dict["proposed_dataset_title"],
        proposed_abstract=data_dict["proposed_abstract"],
        dataset_purpose=data_dict["dataset_purpose"],
        lineage_statement=data_dict["lineage_statement"],
        associated_attributes=data_dict["associated_attributes"],
        feature_description=data_dict["feature_description"],
        data_usage_restrictions=data_dict["data_usage_restrictions"],
        capture_method=data_dict["capture_method"],
        capture_method_detail=data_dict["capture_method_detail"],
    )
    notification_targets = []

    for target in data_dict.get("notification_targets", []):
        target = dcpr_request.DCPRRequestNotificationTarget(
            dcpr_request_id=request.csi_reference_id,
            user_id=target.get("user_id"),
            group_id=target.get("group_id"),
        )
        notification_targets.append(target)

    try:
        model.Session.add(request)
        model.repo.commit()
        request_dataset.dcpr_request_id = request.csi_reference_id
        model.Session.add(request_dataset)

        model.Session.add_all(notification_targets)

        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return request


def dcpr_request_update(context, data_dict):

    logger.debug("Inside the dcpr_request_update action")

    model = context["model"]
    toolkit.check_access("dcpr_request_update_auth", context, data_dict)

    schema = context.get("schema", update_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    if int(data_dict["action_type"]) == DCPRRequestActionType.SAVE.value:
        status = dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    elif int(data_dict["action_type"]) == DCPRRequestActionType.SUBMIT.value:
        status = dcpr_request.DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
        data_dict["nsif_review_date"] = datetime.now()
        data_dict["nsif_reviewer"] = toolkit.g.userobj.id
    elif int(data_dict["action_type"]) == DCPRRequestActionType.ESCALATE_TO_CSI.value:
        status = dcpr_request.DCPRRequestStatus.AWAITING_CSI_REVIEW.value
        data_dict["csi_review_date"] = datetime.now()
        data_dict["csi_moderator"] = toolkit.g.userobj.id
    elif int(data_dict["action_type"]) == DCPRRequestActionType.ACCEPT.value:
        status = dcpr_request.DCPRRequestStatus.ACCEPTED.value
    elif int(data_dict["action_type"]) == DCPRRequestActionType.REJECT.value:
        status = dcpr_request.DCPRRequestStatus.REJECTED.value
    else:
        raise NotImplementedError

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict["request_id"]
    )

    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id == data_dict["request_id"]
    )

    if not request_obj or not request_dataset_obj:
        raise toolkit.ObjectNotFound
    else:
        request_obj.status = status
        if data_dict is not None:
            _copy_dcpr_requests_fields(request_obj, request_dataset_obj, data_dict)

    try:
        model.Session.commit()
        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return request_obj


def dcpr_request_delete(context, data_dict):

    logger.debug("Inside the dcpr_request_delete action")
    model = context["model"]
    toolkit.check_access("dcpr_request_delete_auth", context, data_dict)

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict["request_id"]
    )

    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id == data_dict["request_id"]
    )

    notification_targets = model.Session.query(
        dcpr_request.DCPRRequestNotificationTarget
    ).filter(
        dcpr_request.DCPRRequestNotificationTarget.dcpr_request_id
        == data_dict["request_id"]
    )

    for target in notification_targets:
        target.delete()

    request_dataset_obj.delete()
    model.Session.delete(request_obj)

    try:
        model.Session.commit()
        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return request_obj


def dcpr_geospatial_request_create(context, data_dict):
    model = context["model"]
    toolkit.check_access("dcpr_request_create_auth", context, data_dict)
    logger.debug("Inside the dcpr_request_create action")

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

    q = model.Session.query(dcpr_request.DCPRRequest)

    if user is None:  # show only  moderated requests
        pass
    elif user.sysadmin:  # show all requests
        pass
    else:  # show relevant requests depending on the user's organization
        pass

    limit = data_dict.get("limit", 10)
    offset = data_dict.get("offset", 0)
    dcpr_requests = q.limit(limit).offset(offset).all()

    return dcpr_requests


@toolkit.side_effect_free
def dcpr_request_show(context: typing.Dict, data_dict: typing.Dict) -> typing.List:
    request_id = toolkit.get_or_bust(data_dict, "id")

    request_object = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_object:
        raise toolkit.ObjectNotFound

    toolkit.check_access("dcpr_request_show_auth", context, data_dict)

    request_dict = d.table_dictize(request_object, context)

    return request_dict


def _copy_dcpr_requests_fields(dcpr_request, dcpr_request_dataset, data_dict):

    dcpr_request.csi_moderator = data_dict.get("csi_moderator", None)
    dcpr_request.nsif_reviewer = data_dict.get("nsif_reviewer", None)

    dcpr_request.organization_name = data_dict["organization_name"]
    dcpr_request.organization_level = data_dict["organization_level"]
    dcpr_request.organization_address = data_dict["organization_address"]
    dcpr_request.proposed_project_name = data_dict["proposed_project_name"]
    dcpr_request.additional_project_context = data_dict["additional_project_context"]
    dcpr_request.capture_start_date = data_dict["capture_start_date"]
    dcpr_request.capture_end_date = data_dict["capture_end_date"]
    dcpr_request.cost = data_dict["cost"]
    dcpr_request.spatial_extent = data_dict.get("spatial_extent", None)
    dcpr_request.spatial_resolution = data_dict["spatial_resolution"]
    dcpr_request.data_capture_urgency = data_dict["data_capture_urgency"]
    dcpr_request.additional_information = data_dict["additional_information"]
    dcpr_request.nsif_review_date = data_dict.get("nsif_review_date", None)
    dcpr_request.nsif_recommendation = data_dict.get("nsif_recommendation", None)
    dcpr_request.nsif_review_notes = data_dict.get("nsif_review_notes", None)
    dcpr_request.nsif_review_additional_documents = data_dict.get(
        "nsif_review_additional_documents", None
    )
    dcpr_request.csi_moderation_notes = data_dict.get("csi_moderation_notes", None)
    dcpr_request.csi_moderation_additional_documents = data_dict.get(
        "csi_moderation_additional_documents", None
    )
    dcpr_request.csi_moderation_date = data_dict.get("csi_moderation_date", None)

    dcpr_request_dataset.dataset_custodian = data_dict.get("dataset_custodian", False)
    dcpr_request_dataset.data_type = data_dict["data_type"]
    dcpr_request_dataset.proposed_dataset_title = data_dict["proposed_dataset_title"]
    dcpr_request_dataset.proposed_abstract = data_dict["proposed_abstract"]
    dcpr_request_dataset.dataset_purpose = data_dict["dataset_purpose"]
    dcpr_request_dataset.lineage_statement = data_dict["lineage_statement"]
    dcpr_request_dataset.associated_attributes = data_dict["associated_attributes"]
    dcpr_request_dataset.feature_description = data_dict["feature_description"]
    dcpr_request_dataset.data_usage_restrictions = data_dict["data_usage_restrictions"]
    dcpr_request_dataset.capture_method = data_dict["capture_method"]
    dcpr_request_dataset.capture_method_detail = data_dict["capture_method_detail"]
