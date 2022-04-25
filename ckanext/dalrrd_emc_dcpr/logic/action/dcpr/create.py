import logging

from ckan.plugins import toolkit
from sqlalchemy import exc

from ...schema import create_dcpr_request_schema
from ....model import dcpr_error_report, dcpr_request

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
    toolkit.check_access("dcpr_request_create_auth", context, data_dict)
    schema = context.get("schema", create_dcpr_request_schema())
    data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    request = dcpr_request.DCPRRequest(
        owner_user=data_dict["owner_user"],
        csi_moderator=data_dict.get("csi_moderator", None),
        nsif_reviewer=data_dict.get("nsif_reviewer", None),
        status=dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value,
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
        model = context["model"]
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
