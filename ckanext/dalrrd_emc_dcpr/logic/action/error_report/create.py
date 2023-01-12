import logging

from ckan.plugins import toolkit

from .... import error_report_dictization
from ...schema import create_error_report_schema
from ....model import error_report
from ....constants import ErrorReportStatus

logger = logging.getLogger(__name__)


def error_report_create(context, data_dict):
    toolkit.check_access("error_report_create_auth", context, data_dict)
    logger.debug("Inside the error_report_create action")

    logger.info(f"Metadata record {data_dict.get('metadata_record')}")

    model = context["model"]
    schema = context.get("schema", create_error_report_schema())

    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)

    toolkit.check_access("error_report_create_auth", context, validated_data)

    validated_data.update(
        {
            "owner_user": context["auth_user_obj"].id,
            "status": ErrorReportStatus.SUBMITTED.value,
        }
    )

    error_report_obj = error_report_dictization.error_report_dict_save(
        validated_data, context
    )
    model.Session.commit()

    return toolkit.get_action("error_report_show")(
        context=context,
        data_dict={"csi_reference_id": error_report_obj.csi_reference_id},
    )
