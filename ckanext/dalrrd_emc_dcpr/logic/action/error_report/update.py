import datetime as dt
import logging
import typing

from ckan.plugins import toolkit

from ... import schema as error_schema
from .... import error_report_dictization
from ....model import error_report
from ....constants import ErrorReportStatus

logger = logging.getLogger(__name__)


def error_report_update_by_owner(context, data_dict):
    schema = error_schema.update_error_report_by_owner_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    validated_data["csi_reference_id"] = data_dict["csi_reference_id"]
    validated_data["status"] = ErrorReportStatus.SUBMITTED.value

    toolkit.check_access("error_report_update_by_owner_auth", context, validated_data)
    validated_data["owner_user"] = context["auth_user_obj"].id

    context["updated_by"] = "owner"
    error_report_obj = error_report_dictization.error_report_dict_save(
        validated_data, context
    )
    context["model"].Session.commit()

    return error_report_dictization.error_report_dictize(error_report_obj, context)


def error_report_update_by_nsif(context, data_dict):

    schema = error_schema.update_error_report_by_owner_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    validated_data["csi_reference_id"] = data_dict["csi_reference_id"]
    toolkit.check_access("error_report_update_by_nsif_auth", context, validated_data)

    if ErrorReportStatus(validated_data["status"]) in [
        ErrorReportStatus.APPROVED,
        ErrorReportStatus.REJECTED,
    ]:
        raise toolkit.NotAuthorized

    validated_data.update(
        {
            "nsif_reviewer": context["auth_user_obj"].id,
            "nsif_moderation_date": dt.datetime.now(dt.timezone.utc),
        }
    )
    error_report_obj = error_report_dictization.error_report_dict_save(
        validated_data, context
    )
    context["model"].Session.commit()

    return error_report_dictization.error_report_dictize(error_report_obj, context)


def error_report_nsif_moderate(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:

    schema = error_schema.moderate_error_report_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access("error_report_nsif_moderate_auth", context, validated_data)
    validated_data.update(nsif_moderation_date=dt.datetime.now(dt.timezone.utc))
    report_obj = (
        context["model"]
        .Session.query(error_report.ErrorReport)
        .get(validated_data["csi_reference_id"])
    )

    if report_obj is not None:
        if ErrorReportStatus(report_obj.status) in [
            ErrorReportStatus.APPROVED,
            ErrorReportStatus.REJECTED,
        ]:
            raise toolkit.NotAuthorized
        try:

            action_status = {
                "APPROVE": "APPROVED",
                "REJECT": "REJECTED",
                "REQUEST_MODIFICATION": "MODIFICATION_REQUESTED",
            }
            report_obj.status = ErrorReportStatus(
                action_status[str(data_dict.get("action"))]
            ).value
            report_obj.nsif_moderation_date = dt.datetime.now(dt.timezone.utc)

        except (KeyError, ValueError):
            result = toolkit.abort(status_code=404, detail="Invalid moderation action")
        else:
            if context["auth_user_obj"].sysadmin:
                report_obj.nsif_reviewer = context["auth_user_obj"].id
            context["model"].Session.commit()

            result = toolkit.get_action("error_report_show")(context, validated_data)

    else:
        raise toolkit.ObjectNotFound

    return result
