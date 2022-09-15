import logging
import typing

from ckan.plugins import toolkit
from ...model import error_report
from ...constants import ErrorReportStatus

logger = logging.getLogger(__name__)


def error_report_create_auth(
        context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    db_user = context["auth_user_obj"]
    result = {"success": False}
    if db_user.sysadmin:
        result["success"] = True
    else:
        result = {"success": len(db_user.get_groups()) > 0}
    return result


def error_report_update_by_owner_auth(
        context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    request_obj = error_report.ErrorReport.get(data_dict["csi_reference_id"])

    result = {"success": request_obj.owner_user == context["auth_user_obj"].id}
    return result



def error_report_update_by_nsif_auth(
        context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    request_obj = error_report.ErrorReport.get(data_dict["csi_reference_id"])

    is_nsif_reviewer = toolkit.h["emc_user_is_org_member"] \
        ("nsif", context["auth_user_obj"], role="editor")

    result = {"success": (is_nsif_reviewer and
                          request_obj.status == ErrorReportStatus.SUBMITTED.value)}
    return result


def error_report_nsif_moderate_auth(
        context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    """ Moderation authentication for error report"""
    request_obj = error_report.ErrorReport.get(data_dict["csi_reference_id"])
    result = {"success": False}
    user = context["auth_user_obj"]
    is_nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    if request_obj is not None:
        if request_obj.status == ErrorReportStatus.SUBMITTED.value:
            if context["auth_user_obj"].sysadmin:
                result["success"] = True
            elif context["auth_user_obj"].id == request_obj.owner_user:
                result["msg"] = toolkit._(
                    "The report owner cannot be involved in the moderation stage"
                )
            elif is_nsif_reviewer:
                result["success"] = True
            else:
                result["msg"] = toolkit._(
                    "Current user is not authorized to moderate this report"
                )
        else:
            result["msg"] = toolkit._(
                "Report cannot currently be moderated on behalf of the NSIF"
            )
    else:
        result["msg"] = toolkit._("Request not found")
    return result


def my_error_reports_auth(
        context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
):
    result = {"success": False}
    if context["auth_user_obj"].sysadmin:
        result["success"] = True
    else:
        result["success"] = toolkit.h["emc_user_is_org_member"](
            'nsif', context["auth_user_obj"]
        )
    return result


def error_report_submitted_auth(
        context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
):
    result = {"success": False}
    if context["auth_user_obj"].sysadmin:
        result["success"] = True
    else:
        result["success"] = toolkit.h["emc_user_is_org_member"](
            'nsif', context["auth_user_obj"]
        )
    return result


def error_report_delete_auth(
        context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    """
    Error reports can be deleted by NSIF representative
    """

    report_id = toolkit.get_or_bust(data_dict, "csi_reference_id")
    report_obj = error_report.ErrorReport.get(report_id)
    result = {"success": False}
    if report_obj is not None:
        is_nsif_reviewer = context["auth_user_obj"].id == report_obj.nsif_reviewer
        report_submitted = report_obj.status == ErrorReportStatus.SUBMITTED.value
        if (is_nsif_reviewer or context["auth_user_obj"].sysadmin) and report_submitted:
            result["success"] = True
    else:
        result["msg"] = toolkit._("Error report not found")
    return result
