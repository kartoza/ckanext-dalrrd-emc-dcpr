import datetime as dt
import logging
import typing

from ckan.plugins import toolkit
from sqlalchemy import exc

from ....constants import DCPRRequestStatus
from ... import schema as dcpr_schema
from ....model import dcpr_request
from .... import dcpr_dictization

logger = logging.getLogger(__name__)


def dcpr_request_update_by_owner(context, data_dict):
    logger.debug(f"raw_data_dict input to the CKAN action: {data_dict}")
    schema = dcpr_schema.update_dcpr_request_by_owner_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    logger.debug(f"{validated_data=}")
    logger.debug(f"{errors=}")
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_update_by_owner_auth", context, validated_data)
    validated_data["owner_user"] = context["auth_user_obj"].id
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    context["model"].Session.commit()
    # TODO: would be nice to add an activity here
    return dcpr_dictization.dcpr_request_dictize(request_obj, context)


def dcpr_request_update_by_nsif(context, data_dict):
    """Update a DCPR request's NSIF-related fields.

    Some fields of a DCPR request can only be modified by members of the NSIF
    organization. Additionally, once a specific user starts updating the request, it
    becomes its nsif_reviewer and all further updates by the NSIF must be done by that
    user.

    """

    schema = dcpr_schema.update_dcpr_request_by_nsif_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_update_by_nsif_auth", context, validated_data)
    validated_data.update(
        {
            "nsif_reviewer": context["auth_user_obj"].id,
            "nsif_review_date": dt.datetime.now(dt.timezone.utc),
        }
    )
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    context["model"].Session.commit()
    # TODO: would be nice to add an activity here
    return dcpr_dictization.dcpr_request_dictize(request_obj, context)


def dcpr_request_update_by_csi(context, data_dict):
    """Update a DCPR request's CSI-related fields.

    Some fields of a DCPR request can only be modified by members of the CSI
    organization. Additionally, once a specific user starts updating the request, it
    becomes its csi_moderator and all further updates by the CSI must be done by that
    user.

    """

    schema = dcpr_schema.update_dcpr_request_by_csi_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_update_by_csi_auth", context, validated_data)
    validated_data.update(
        {
            "csi_moderator": context["auth_user_obj"].id,
            "csi_moderation_date": dt.datetime.now(dt.timezone.utc),
        }
    )
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    context["model"].Session.commit()
    # TODO: would be nice to add an activity here
    return dcpr_dictization.dcpr_request_dictize(request_obj, context)


def dcpr_request_submit(context, data_dict):
    """Submit a DCPR request.

    By submitting a DCPR request, it is marked as ready for review by the SASDI
    organizations.

    """

    schema = dcpr_schema.dcpr_request_submit_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access("dcpr_request_submit_auth", context, validated_data)
    validated_data["submission_date"] = dt.datetime.now(dt.timezone.utc)
    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    logger.debug(f"{request_obj=}")
    if request_obj is not None:
        next_status = DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
        request_obj.status = next_status
        model.Session.commit()
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def dcpr_request_nsif_moderate(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    """Provide the NSIF's moderation for a DCPR request.

    By moderating a DCPR request, it is either rejected or marked as reviewed by the
    NSIF and ready for further moderation by the CSI.

    """

    return _moderate(
        context,
        data_dict,
        auth_function="dcpr_request_nsif_moderate_auth",
        approval_status=DCPRRequestStatus.AWAITING_CSI_REVIEW,
        nsif_moderation_date=dt.datetime.now(dt.timezone.utc),
    )


def dcpr_request_csi_moderate(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _moderate(
        context,
        data_dict,
        auth_function="dcpr_request_csi_moderate_auth",
        csi_moderation_date=dt.datetime.now(dt.timezone.utc),
    )


def _moderate(
    context: typing.Dict,
    data_dict: typing.Dict,
    auth_function: str,
    approval_status: DCPRRequestStatus = DCPRRequestStatus.ACCEPTED,
    rejection_status: DCPRRequestStatus = DCPRRequestStatus.REJECTED,
    **additional_data,
) -> typing.Dict:
    logger.debug(f"inside _moderate - {data_dict=}")
    schema = dcpr_schema.moderate_dcpr_request_schema()
    logger.debug(f"{schema=}")
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    logger.debug(f"validated_data - {validated_data=}")
    logger.debug(f"errors - {errors=}")
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access(auth_function, context, validated_data)
    validated_data.update(additional_data)
    request_obj = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .get(validated_data["csi_reference_id"])
    )
    if request_obj is not None:
        next_status = (
            approval_status if validated_data["approved"] else rejection_status
        )
        request_obj.status = next_status.value
        context["model"].Session.commit()
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def claim_dcpr_request_nsif_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _claim_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_claim_nsif_reviewer_auth",
        next_status=DCPRRequestStatus.UNDER_NSIF_REVIEW,
        reviewer_request_attribute="nsif_reviewer",
    )


def claim_dcpr_request_csi_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _claim_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_claim_csi_moderator_auth",
        next_status=DCPRRequestStatus.UNDER_CSI_REVIEW,
        reviewer_request_attribute="csi_moderator",
    )


def _claim_reviewer(
    context: typing.Dict,
    data_dict: typing.Dict,
    auth_function: str,
    next_status: DCPRRequestStatus,
    reviewer_request_attribute: str,
) -> typing.Dict:
    schema = dcpr_schema.claim_reviewer_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access(auth_function, context, validated_data)
    model = context["model"]
    request_obj = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .get(validated_data["csi_reference_id"])
    )
    if request_obj is not None:
        request_obj.status = next_status.value
        setattr(request_obj, reviewer_request_attribute, context["auth_user_obj"].id)
        model.Session.commit()
    else:
        raise toolkit.ObjectNotFound
    # TODO: would be nice to add an activity here
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def resign_dcpr_request_nsif_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _resign_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_resign_nsif_reviewer_auth",
        next_status=DCPRRequestStatus.AWAITING_NSIF_REVIEW,
    )


def resign_dcpr_request_csi_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _resign_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_resign_csi_reviewer_auth",
        next_status=DCPRRequestStatus.AWAITING_CSI_REVIEW,
    )


def _resign_reviewer(
    context: typing.Dict,
    data_dict: typing.Dict,
    auth_function: str,
    next_status: DCPRRequestStatus,
) -> typing.Dict:
    schema = dcpr_schema.resign_reviewer_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access(auth_function, context, validated_data)
    request_obj = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .get(validated_data["csi_reference_id"])
    )
    if request_obj is not None:
        request_obj.status = next_status.value
        context["model"].Session.commit()
    else:
        raise toolkit.ObjectNotFound
    # TODO: would be nice to add an activity here
    return toolkit.get_action("dcpr_request_show")(context, validated_data)
