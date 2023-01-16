import logging

from ckan.plugins import toolkit
from sqlalchemy import exc

from .... import dcpr_dictization
from ...schema import create_dcpr_request_schema
from ....model import dcpr_error_report, dcpr_request
from ....constants import (
    DcprManagementActivityType,
    DCPRRequestStatus,
)
from .. import create_dcpr_management_activity

logger = logging.getLogger(__name__)


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
    logger.debug(f"{data_dict=}")
    model = context["model"]
    schema = context.get("schema", create_dcpr_request_schema())
    logger.debug(f"{schema=}")
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    logger.debug(f"{errors=}")
    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)

    # add validation error to capture_end_date
    date_start = data_dict["capture_start_date"]
    date_end = data_dict["capture_end_date"]
    if date_end < date_start:
        raise toolkit.ValidationError(
            {
                "capture_end_date": [
                    "Invalid value. Please select a date after capture start date."
                ],
            }
        )
    toolkit.check_access("dcpr_request_create_auth", context, validated_data)

    # after validation of user-supplied data, enrich the data dict with additional
    # required attributes, like the request owner, status, etc.
    validated_data.update(
        {
            "owner_user": context["auth_user_obj"].id,
            "status": DCPRRequestStatus.UNDER_PREPARATION.value,
        }
    )
    logger.debug(f"{validated_data=}")
    context["updated_by"] = "owner"
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    model.Session.commit()
    logger.debug(f"{request_obj=}")
    create_dcpr_management_activity(
        request_obj,
        activity_type=DcprManagementActivityType.CREATE_DCPR_REQUEST,
        context=context,
    )
    return toolkit.get_action("dcpr_request_show")(
        context=context.copy(),
        data_dict={"csi_reference_id": request_obj.csi_reference_id},
    )


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
