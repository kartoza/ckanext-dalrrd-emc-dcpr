import logging
import typing

from ckan.plugins import toolkit
from ...model import dcpr_request as dcpr_request
from ...constants import DCPRRequestStatus, CSI_ORG_NAME, NSIF_ORG_NAME

logger = logging.getLogger(__name__)


def dcpr_request_list_private_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
):
    """Authorize listing private DCPR requests.

    Only users that are members of an organization are allowed to have private DCPR
    requests.

    """
    return dcpr_request_create_auth(context, data_dict)


@toolkit.auth_allow_anonymous_access
def dcpr_request_list_public_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    """Authorize listing public DCPR requests"""
    return {"success": True}


def dcpr_request_list_pending_csi_auth():
    """Authorize listing DCPR requests which are under evaluation by CSI"""
    # FIXME: Implement this
    return {"success": False}


def dcpr_request_list_pending_nsif_auth():
    """Authorize listing DCPR requests which are under evaluation by NSIF"""
    # FIXME: Implement this
    return {"success": False}


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
    """Authorize DCPR request creation.

    Creation of DCPR requests is reserved for logged in users that have been granted
    membership of an organization.

    NOTE: The implementation does not need to check if the user is logged in because
    CKAN already does that for us, as per:

    https://docs.ckan.org/en/2.9/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IAuthFunctions

    """

    db_user = context["auth_user_obj"]
    member_of_orgs = len(db_user.get_groups()) > 0
    result = {"success": member_of_orgs}
    return result


@toolkit.auth_allow_anonymous_access
def dcpr_request_show_auth(context: typing.Dict, data_dict: typing.Dict) -> typing.Dict:
    logger.debug("Inside dcpr_request_show_auth")
    result = {"success": False}
    request_obj = dcpr_request.DCPRRequest.get(
        csi_reference_id=data_dict.get("csi_reference_id")
    )
    if request_obj:
        unauthorized_msg = toolkit._("You are not authorized to view this request")
        published_statuses = (
            DCPRRequestStatus.ACCEPTED.value,
            DCPRRequestStatus.REJECTED.value,
        )
        csi_statuses = (
            DCPRRequestStatus.AWAITING_CSI_REVIEW.value,
            DCPRRequestStatus.UNDER_CSI_REVIEW.value,
        )
        nsif_statuses = (
            DCPRRequestStatus.AWAITING_NSIF_REVIEW.value,
            DCPRRequestStatus.UNDER_NSIF_REVIEW.value,
        )
        if context["auth_user_obj"].id == request_obj.owner_user:
            # this is the owner, allow
            result["success"] = True
        elif request_obj.status in published_statuses:
            # request has already been moderated, so everyone can see it
            result["success"] = True
        elif request_obj.status == DCPRRequestStatus.UNDER_PREPARATION.value:
            # user is not the owner and the request has not been submitted yet, deny
            result["msg"] = unauthorized_msg
        elif request_obj.status in csi_statuses:
            # user is not the owner, but if it is member of CSI, then allow
            is_csi_member = toolkit.h["emc_user_is_org_member"](
                CSI_ORG_NAME, context["auth_user_obj"]
            )
            if is_csi_member:
                result["success"] = True
            else:
                result["msg"] = unauthorized_msg
        elif request_obj.status in nsif_statuses:
            # user is not the owner, but if it is member of NSIF, then allow
            is_nsif_member = toolkit.h["emc_user_is_org_member"](
                NSIF_ORG_NAME, context["auth_user_obj"]
            )
            if is_nsif_member:
                result["success"] = True
            else:
                result["msg"] = unauthorized_msg
    else:
        result["msg"] = toolkit._("DCPR request not found")
    return result


def dcpr_request_update_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_update auth")

    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.id == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == DCPRRequestStatus.UNDER_PREPARATION.value
    )

    nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", user, role="editor")

    request_escalated_to_csi = (
        request_obj.status == DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )
    request_submitted = (
        request_obj.status == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
    )

    success = (
        (owner and request_in_preparation)
        or (csi_reviewer and request_escalated_to_csi)
        or (nsif_reviewer and request_submitted)
    )

    return {"success": success}


def dcpr_request_submit_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_submit auth")

    user = context["auth_user_obj"]

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("id", None)
    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.id == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == DCPRRequestStatus.UNDER_PREPARATION.value
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
        request_obj.status == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
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
        request_obj.status == DCPRRequestStatus.AWAITING_CSI_REVIEW.value
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
        request_obj.status == DCPRRequestStatus.AWAITING_CSI_REVIEW.value
    )
    request_submitted = (
        request_obj.status == DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
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

    request_id = data_dict.get("id", None)

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

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

    if not user or not data_dict:
        return {"success": False}

    request_id = data_dict.get("request_id", None)

    request_obj = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)
    if not request_obj:
        return {"success": False, "msg": toolkit._("Request not found")}

    owner = user.get("id") == request_obj.owner_user
    request_in_preparation = (
        request_obj.status == DCPRRequestStatus.UNDER_PREPARATION.value
    )

    if not owner or not request_in_preparation:
        return {"success": False}

    return {"success": True}
