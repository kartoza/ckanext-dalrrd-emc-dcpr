import datetime as dt
import logging
import typing

from ckan.plugins import toolkit

from .... import jobs
from ....constants import ErrorReportStatus, ErrorReportModerationAction
from ... import schema as error_schema
from ....model import error_report
from .... import error_report_dictization

logger = logging.getLogger(__name__)


def error_report_update_by_owner(context, data_dict):
    schema = error_schema.update_error_report_by_owner_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

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
    toolkit.check_access("error_report_update_by_nsif_auth", context, validated_data)
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
