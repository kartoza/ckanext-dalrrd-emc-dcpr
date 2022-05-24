import datetime as dt
import logging
import typing

from ckan.plugins import toolkit

from ....constants import (
    DcprRequestModerationAction,
    DCPRRequestStatus,
)
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
    context["updated_by"] = "owner"
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
        # next_status = DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
        # request_obj.status = next_status
        _update_dcpr_request_status(request_obj)
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
        # approval_status=DCPRRequestStatus.AWAITING_CSI_REVIEW,
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
    # approval_status: DCPRRequestStatus = DCPRRequestStatus.ACCEPTED,
    # rejection_status: DCPRRequestStatus = DCPRRequestStatus.REJECTED,
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
        try:
            moderation_action = DcprRequestModerationAction(
                validated_data.get("action")
            )
        except ValueError:
            result = toolkit.abort(status_code=404, detail="Invalid moderation action")
        else:
            _update_dcpr_request_status(
                request_obj, transition_action=moderation_action
            )
            # next_status = (
            #     approval_status if validated_data["approved"] else rejection_status
            # )
            # request_obj.status = next_status.value
            context["model"].Session.commit()
            result = toolkit.get_action("dcpr_request_show")(context, validated_data)
    else:
        raise toolkit.ObjectNotFound
    return result


def claim_dcpr_request_nsif_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _claim_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_claim_nsif_reviewer_auth",
        # next_status=DCPRRequestStatus.UNDER_NSIF_REVIEW,
        reviewer_request_attribute="nsif_reviewer",
    )


def claim_dcpr_request_csi_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _claim_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_claim_csi_moderator_auth",
        # next_status=DCPRRequestStatus.UNDER_CSI_REVIEW,
        reviewer_request_attribute="csi_moderator",
    )


def _claim_reviewer(
    context: typing.Dict,
    data_dict: typing.Dict,
    auth_function: str,
    # next_status: DCPRRequestStatus,
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
        _update_dcpr_request_status(request_obj)
        # request_obj.status = next_status.value
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
        # next_status=DCPRRequestStatus.AWAITING_NSIF_REVIEW,
    )


def resign_dcpr_request_csi_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return _resign_reviewer(
        context,
        data_dict,
        auth_function="dcpr_request_resign_csi_reviewer_auth",
        # next_status=DCPRRequestStatus.AWAITING_CSI_REVIEW,
    )


def _resign_reviewer(
    context: typing.Dict,
    data_dict: typing.Dict,
    auth_function: str,
    # next_status: DCPRRequestStatus,
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
        _update_dcpr_request_status(
            request_obj, transition_action=DcprRequestModerationAction.RESIGN
        )
        # request_obj.status = next_status.value
        context["model"].Session.commit()
    else:
        raise toolkit.ObjectNotFound
    # TODO: would be nice to add an activity here
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def _update_dcpr_request_status(
    dcpr_request_obj: dcpr_request.DCPRRequest,
    transition_action: typing.Optional[DcprRequestModerationAction] = None,
) -> dcpr_request.DCPRRequest:
    current_status = DCPRRequestStatus(dcpr_request_obj.status)
    logger.debug(f"{current_status=}")
    try:
        next_status = _determine_next_dcpr_request_status(
            current_status, transition_action
        )
        logger.debug(f"{next_status=}")
    except NotImplementedError:
        logger.exception(msg="Unable to update DCPR request status")
    else:
        if next_status is not None:
            dcpr_request_obj.status = next_status.value
    return dcpr_request_obj


def _determine_next_dcpr_request_status(
    current_status: DCPRRequestStatus,
    transition_action: typing.Optional[DcprRequestModerationAction] = None,
) -> typing.Optional[DCPRRequestStatus]:
    # statuses related to request preparation/modification by the owner
    if current_status == DCPRRequestStatus.UNDER_PREPARATION:
        next_status = DCPRRequestStatus.AWAITING_NSIF_REVIEW
    elif current_status == DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF:
        next_status = DCPRRequestStatus.UNDER_NSIF_REVIEW
    elif current_status == DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI:
        next_status = DCPRRequestStatus.UNDER_CSI_REVIEW

    # statuses related to awaiting for a user to claim the role of reviewer
    elif current_status == DCPRRequestStatus.AWAITING_NSIF_REVIEW:
        next_status = DCPRRequestStatus.UNDER_NSIF_REVIEW
    elif current_status == DCPRRequestStatus.AWAITING_CSI_REVIEW:
        next_status = DCPRRequestStatus.UNDER_CSI_REVIEW

    # statuses related to review and moderation
    elif current_status == DCPRRequestStatus.UNDER_NSIF_REVIEW:
        if transition_action == DcprRequestModerationAction.APPROVE:
            next_status = DCPRRequestStatus.AWAITING_CSI_REVIEW
        elif transition_action == DcprRequestModerationAction.REJECT:
            next_status = DCPRRequestStatus.REJECTED
        elif transition_action == DcprRequestModerationAction.REQUEST_CLARIFICATION:
            next_status = DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_NSIF
        elif transition_action == DcprRequestModerationAction.RESIGN:
            next_status = DCPRRequestStatus.AWAITING_NSIF_REVIEW
        else:
            raise NotImplementedError
    elif current_status == DCPRRequestStatus.UNDER_CSI_REVIEW:
        if transition_action == DcprRequestModerationAction.APPROVE:
            next_status = DCPRRequestStatus.ACCEPTED
        elif transition_action == DcprRequestModerationAction.REJECT:
            next_status = DCPRRequestStatus.REJECTED
        elif transition_action == DcprRequestModerationAction.REQUEST_CLARIFICATION:
            next_status = DCPRRequestStatus.UNDER_MODIFICATION_REQUESTED_BY_CSI
        elif transition_action == DcprRequestModerationAction.RESIGN:
            next_status = DCPRRequestStatus.AWAITING_CSI_REVIEW
        else:
            raise NotImplementedError

    # final statuses
    elif current_status in (DCPRRequestStatus.ACCEPTED, DCPRRequestStatus.REJECTED):
        next_status = None

    else:
        raise NotImplementedError
    return next_status
