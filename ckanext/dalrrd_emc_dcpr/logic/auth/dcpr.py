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

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.get("id") == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    )

    return {"success": owner and not request_in_preparation}


def dcpr_request_submit_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_submit auth")

    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.get("id") == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    )

    return {"success": (owner and request_in_preparation)}


def dcpr_request_escalate_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_escalate auth")

    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    request_submitted = (
        request_obj.status == dcpr_request.DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )

    return {"success": nsif_reviewer and request_submitted}


def dcpr_request_accept_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_accept auth")

    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", user, role="editor")
    request_escalated_to_csi = (
        request_obj.status == dcpr_request.DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )

    return {
        "success": csi_reviewer and request_escalated_to_csi,
    }


def dcpr_request_reject_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_reject auth")

    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", user, role="editor")

    request_escalated_to_csi = (
        request_obj.status == dcpr_request.DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )
    request_submitted = (
        request_obj.status == dcpr_request.DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )

    return {
        "success": (csi_reviewer and request_escalated_to_csi)
        or (nsif_reviewer and request_submitted)
    }


def dcpr_request_edit_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_edit auth")
    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}
    request_id = data_dict.get("request_id", None)

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.get("id") == request_obj.owner_user
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

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)
    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.get("id") == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == dcpr_request.DCPRRequestStatus.UNDER_PREPARATION.value
    )

    if not owner or not request_in_preparation:
        return {"success": False}

    return {"success": True}
