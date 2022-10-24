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
    result = {"success": db_user is not None}
    return result


@toolkit.auth_allow_anonymous_access
def error_report_show_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    db_user = context["auth_user_obj"]
    error_report_obj = (
        error_report.ErrorReport.get(csi_reference_id=data_dict.get("csi_reference_id"))
        if data_dict
        else None
    )

    is_nsif_reviewer = toolkit.h["emc_user_is_org_member"](
        "nsif", context["auth_user_obj"]
    )
    result = {"success": False}
    if not db_user:
        if error_report_obj and error_report_obj.status in [
            ErrorReportStatus.APPROVED.value,
            ErrorReportStatus.REJECTED.value,
        ]:
            result = {"success": True}
    else:
        if db_user.sysadmin:
            result["success"] = True
        else:
            if error_report_obj is not None:
                if error_report_obj.status in [
                    ErrorReportStatus.SUBMITTED.value,
                    ErrorReportStatus.MODIFICATION_REQUESTED.value,
                ]:
                    result = {
                        "success": is_nsif_reviewer
                        or error_report_obj.owner_user == db_user.id
                    }
                elif error_report_obj.status in [
                    ErrorReportStatus.APPROVED.value,
                    ErrorReportStatus.REJECTED.value,
                ]:
                    result = {"success": True}
                else:
                    result = {"success": False}
    return result


def error_report_update_by_owner_auth(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    error_report_obj = error_report.ErrorReport.get(
        csi_reference_id=data_dict.get("csi_reference_id")
    )
    result = {"success": False}
    if error_report_obj is not None:
        if error_report_obj.status in [
            ErrorReportStatus.APPROVED.value,
            ErrorReportStatus.REJECTED.value,
        ]:
            result = {"success": False}
        else:
            result = {
                "success": error_report_obj.owner_user == context["auth_user_obj"].id
                and error_report_obj.status
                == ErrorReportStatus.MODIFICATION_REQUESTED.value
            }
    return result


def error_report_update_by_nsif_auth(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    error_report_obj = error_report.ErrorReport.get(
        csi_reference_id=data_dict.get("csi_reference_id")
    )
    result = {"success": False}
    if error_report_obj is not None:
        if context["auth_user_obj"].sysadmin:
            result["success"] = True

        is_nsif_reviewer = toolkit.h["emc_user_is_org_member"](
            "nsif", context["auth_user_obj"], role="editor"
        )

        result = {
            "success": (
                is_nsif_reviewer
                and error_report_obj.status == ErrorReportStatus.SUBMITTED.value
            )
        }
    return result


def error_report_nsif_moderate_auth(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    """Moderation authentication for error report"""
    error_report_obj = error_report.ErrorReport.get(
        csi_reference_id=data_dict.get("csi_reference_id")
    )
    result = {"success": False}
    user = context["auth_user_obj"]
    is_nsif_reviewer = toolkit.h["emc_user_is_org_member"]("nsif", user, role="editor")
    if error_report_obj is not None:
        if error_report_obj.status == ErrorReportStatus.SUBMITTED.value:
            if user.sysadmin:
                result["success"] = True
            elif user.id == error_report_obj.owner_user:
                result["msg"] = toolkit._(
                    "The report owner cannot be involved in the moderation stage"
                )
            elif is_nsif_reviewer:
                # NSIF users should only review other
                # users reports not their own reports.
                result["success"] = user.id != error_report_obj.owner_user
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

    user = context["auth_user_obj"]
    result = {"success": user is not None}

    return result


def error_report_submitted_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
):
    result = {"success": False}
    if context["auth_user_obj"].sysadmin:
        result["success"] = True
    else:
        result["success"] = toolkit.h["emc_user_is_org_member"](
            "nsif", context["auth_user_obj"]
        )
    return result


@toolkit.auth_allow_anonymous_access
def error_report_list_public_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    return {"success": True}


@toolkit.auth_allow_anonymous_access
def rejected_error_reports_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    return {"success": True}


def my_error_report_list_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    return {"success": True}


def error_report_delete_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    """
    Error reports can be deleted by NSIF representative
    """

    report_id = toolkit.get_or_bust(data_dict, "csi_reference_id")
    report_obj = error_report.ErrorReport.get(csi_reference_id=report_id)
    result = {"success": False}
    if report_obj is not None:
        owner_user = context["auth_user_obj"].id == report_obj.owner_user
        report_submitted = report_obj.status in [
            ErrorReportStatus.SUBMITTED.value,
            ErrorReportStatus.MODIFICATION_REQUESTED.value,
        ]
        if (owner_user or context["auth_user_obj"].sysadmin) and report_submitted:
            result["success"] = True
    else:
        result["success"] = False
    return result
