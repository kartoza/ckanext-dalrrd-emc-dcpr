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
        result = { "success": len(db_user.get_groups()) > 0}
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
        is_owner = context["auth_user_obj"].id == report_obj.owner_user
        report_submitted = (
            report_obj.status == ErrorReportStatus.SUBMITTED.value
        )
        if (is_owner or context["auth_user_obj"].sysadmin) and report_submitted:
            result["success"] = True
    else:
        result["msg"] = toolkit._("Request not found")
    return result