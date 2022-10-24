import logging

from ckan.plugins import toolkit

from ....model import error_report
from ...schema import delete_error_report_schema

logger = logging.getLogger(__name__)


def error_report_delete(context, data_dict):
    logger.debug("Inside the error_report_delete action")
    schema = delete_error_report_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)

    validated_data["csi_reference_id"] = data_dict["csi_reference_id"]

    model = context["model"]
    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)

    toolkit.check_access("error_report_delete_auth", context, validated_data)

    error_report_obj = model.Session.query(error_report.ErrorReport).get(
        validated_data["csi_reference_id"]
    )
    model.Session.delete(error_report_obj)
    model.Session.commit()
