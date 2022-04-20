import datetime as dt
import logging

from ckan.plugins import toolkit
from sqlalchemy import exc

from ...schema import update_dcpr_request_schema
from ....model import dcpr_request

logger = logging.getLogger(__name__)


def dcpr_request_update(context, data_dict):
    logger.debug("Inside the dcpr_request_update action")

    model = context["model"]

    toolkit.check_access("dcpr_request_update_auth", context, data_dict)
    schema = context.get("schema", update_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict.get("request_id", None)
    )
    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id
        == data_dict.get("request_id", None)
    )
    if not request_obj or not request_dataset_obj:
        raise toolkit.ObjectNotFound
    else:
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


def dcpr_request_submit(context, data_dict):
    logger.debug("Inside the dcpr_request_submit action")

    model = context["model"]

    toolkit.check_access("dcpr_request_submit_auth", context, data_dict)
    schema = context.get("schema", update_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    status = dcpr_request.DCPRRequestStatus.AWAITING_NSIF_REVIEW.value

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict.get("request_id", None)
    )
    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id
        == data_dict.get("request_id", None)
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


def dcpr_request_escalate(context, data_dict):
    logger.debug("Inside the dcpr_request_escalate action")

    model = context["model"]
    user = context["auth_user_obj"]

    toolkit.check_access("dcpr_request_escalate_auth", context, data_dict)
    schema = context.get("schema", update_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    data_dict["nsif_review_date"] = dt.datetime.now()
    data_dict["nsif_reviewer"] = user.id

    status = dcpr_request.DCPRRequestStatus.AWAITING_CSI_REVIEW.value

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict.get("request_id", None)
    )
    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id
        == data_dict.get("request_id", None)
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


def dcpr_request_accept(context, data_dict):
    logger.debug("Inside the dcpr_request_accept action")

    model = context["model"]
    user = context["auth_user_obj"]

    toolkit.check_access("dcpr_request_accept_auth", context, data_dict)
    schema = context.get("schema", update_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    data_dict["csi_review_date"] = dt.datetime.now()
    data_dict["csi_moderator"] = user.id
    status = dcpr_request.DCPRRequestStatus.ACCEPTED.value

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict.get("request_id", None)
    )
    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id
        == data_dict.get("request_id", None)
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


def dcpr_request_reject(context, data_dict):
    logger.debug("Inside the dcpr_request_reject action")

    model = context["model"]
    user = context["auth_user_obj"]

    toolkit.check_access("dcpr_request_reject_auth", context, data_dict)
    schema = context.get("schema", update_dcpr_request_schema())

    data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", user, role="editor")

    if nsif_reviewer:
        data_dict["nsif_review_date"] = dt.datetime.now()
        data_dict["nsif_reviewer"] = user.id
    elif csi_reviewer:
        data_dict["csi_review_date"] = dt.datetime.now()
        data_dict["csi_moderator"] = user.id
    else:
        raise toolkit.NotAuthorized
    status = dcpr_request.DCPRRequestStatus.REJECTED.value

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict.get("request_id", None)
    )
    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id
        == data_dict.get("request_id", None)
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
