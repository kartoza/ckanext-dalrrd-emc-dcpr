import logging
import typing

from ckan.plugins import toolkit

from ....model import error_report
from .... import error_report_dictization
from ....constants import ErrorReportStatus
from ...schema import show_error_report_schema

logger = logging.getLogger(__name__)


@toolkit.side_effect_free
def error_report_show(context: typing.Dict, data_dict: typing.Dict) -> typing.Dict:
    schema = show_error_report_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("error_report_show_auth", context, validated_data)
    error_report_object = error_report.ErrorReport.get(
        csi_reference_id=validated_data["csi_reference_id"]
    )
    if not error_report_object:
        raise toolkit.ObjectNotFound
    return error_report_dictization.error_report_dictize(error_report_object, context)


@toolkit.side_effect_free
def error_report_list_public(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of public error reports."""
    toolkit.check_access("error_report_list_public_auth", context, data_dict or {})
    relevant_statuses = (ErrorReportStatus.APPROVED.value,)
    return _get_error_report_list(
        context,
        data_dict,
        filter_=error_report.ErrorReport.status.in_(relevant_statuses),
    )


@toolkit.side_effect_free
def rejected_error_reports(context: typing.Dict, data_dict: typing.Dict) -> typing.List:
    """Return a list of rejected error reports."""
    toolkit.check_access("rejected_error_reports_auth", context, data_dict or {})
    relevant_statuses = (ErrorReportStatus.REJECTED.value,)
    return _get_error_report_list(
        context,
        data_dict,
        filter_=error_report.ErrorReport.status.in_(relevant_statuses),
    )


@toolkit.side_effect_free
def my_error_report_list(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.List[typing.Dict]:
    toolkit.check_access("my_error_report_list_auth", context, data_dict or {})
    return _get_error_report_list(
        context,
        data_dict,
        filter_=error_report.ErrorReport.owner_user == context["auth_user_obj"].id,
    )


@toolkit.side_effect_free
def submitted_error_report_list(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List[typing.Dict]:

    toolkit.check_access("error_report_submitted_auth", context, data_dict or {})
    return _get_error_report_list(
        context,
        data_dict,
        filter_=error_report.ErrorReport.status == ErrorReportStatus.SUBMITTED.value,
    )


def _get_error_report_list(
    context: typing.Dict,
    data_dict: typing.Optional[typing.Dict] = None,
    filter_=None,
) -> typing.List[typing.Dict]:
    data_ = data_dict if data_dict is not None else {}
    query = context["model"].Session.query(error_report.ErrorReport)
    if filter_ is not None:
        query = query.filter(filter_)
    query = (
        query.order_by(
            error_report.ErrorReport.status,
            error_report.ErrorReport.request_date,
        )
        .limit(data_.get("limit", 10))
        .offset(data_.get("offset", 0))
    )
    return [
        error_report_dictization.error_report_dictize(i, context) for i in query.all()
    ]
