import logging
import typing

from ckan.plugins import toolkit
from ..action.dcpr import DCPRRequestActionType
from ...model import dcpr_request as dcpr_request

logger = logging.getLogger(__name__)


def dcpr_report_create_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_report_create auth")
    user = context["auth_user_obj"]

    # Only allow creation of dcpr report if there is a user logged in.
    if user:
        return {"success": True}
    return {"success": False}


def dcpr_test(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_test auth")
    return {"success": False}


def dcpr_request_create_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_create auth")
    user = context["auth_user_obj"]
    # Only allow creation of dcpr requests if there is a user logged in and
    # the request is intended to be saved or submitted only.

    action_type = data_dict.get("action_type", None) if data_dict else None
    action_type = int(action_type) if action_type else None
    if user:
        if action_type:
            if (
                action_type == DCPRRequestActionType.SAVE.value
                or action_type == DCPRRequestActionType.SUBMIT.value
            ):
                return {"success": True}
            else:
                return {"success": False}
        else:
            return {"success": True}
    else:
        return {"success": False}


@toolkit.auth_allow_anonymous_access
def dcpr_request_list_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_list auth")
    return {"success": True}


@toolkit.auth_allow_anonymous_access
def dcpr_request_show_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_show auth")
    return {"success": True}


def dcpr_request_update_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_update auth")

    user = context["auth_user_obj"]

    if not user:
        return {"success": False}

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=data_dict["request_id"])

    owner = user.id == request_obj.owner_user
    nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", user, role="editor")

    if not owner and not nsif_reviewer and not csi_reviewer:
        return {"success": False}

    request_in_preparation = (
        request_obj.status == dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    )
    request_submitted = (
        request_obj.status == dcpr_request.DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )
    request_escalated_to_csi = (
        request_obj.status == dcpr_request.DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )
    request_finalized = (
        request_obj.status == dcpr_request.DCPRRequestStatus.ACCEPTED.value
    ) or (request_obj.status == dcpr_request.DCPRRequestStatus.REJECTED.value)

    if request_finalized:
        return {"success": False}

    if int(data_dict["action_type"]) == DCPRRequestActionType.SAVE.value:
        return {
            "success": (owner and request_in_preparation)
            or (nsif_reviewer and request_submitted)
            or (csi_reviewer and request_escalated_to_csi)
        }
    elif int(data_dict["action_type"]) == DCPRRequestActionType.SUBMIT.value:
        return {"success": owner and not request_submitted}
    elif int(data_dict["action_type"]) == DCPRRequestActionType.ESCALATE_TO_CSI.value:
        return {"success": nsif_reviewer and request_submitted}
    elif int(data_dict["action_type"]) == DCPRRequestActionType.ACCEPT.value:
        return {
            "success": csi_reviewer and request_escalated_to_csi,
        }
    elif int(data_dict["action_type"]) == DCPRRequestActionType.REJECT.value:
        return {
            "success": (csi_reviewer and request_escalated_to_csi)
            or (nsif_reviewer and request_submitted)
        }
    else:
        return {"success": False}

    return {"success": False}


def dcpr_request_edit_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_edit auth")
    user = context["auth_user_obj"]

    if not user:
        return {"success": False}

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=data_dict["request_id"])

    owner = user.id == request_obj.owner_user
    nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", user, role="editor")

    if not owner and not nsif_reviewer and not csi_reviewer:
        return {"success": False}

    return {"success": True}


def dcpr_request_delete_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_delete auth")

    user = context["auth_user_obj"]

    if not user:
        return {"success": False}

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=data_dict["request_id"])

    owner = user.id == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    )

    if not owner or not request_in_preparation:
        return {"success": False}

    return {"success": True}
