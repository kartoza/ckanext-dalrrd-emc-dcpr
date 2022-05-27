import logging

from ckan.plugins import toolkit

from ....constants import DcprManagementActivityType
from ....model import dcpr_request
from ...schema import delete_dcpr_request_schema
from .. import create_dcpr_management_activity

logger = logging.getLogger(__name__)


def dcpr_request_delete(context, data_dict):
    logger.debug("Inside the dcpr_request_delete action")
    schema = delete_dcpr_request_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    model = context["model"]
    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)

    toolkit.check_access("dcpr_request_delete_auth", context, validated_data)

    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    model.Session.delete(request_obj)
    model.Session.commit()
    create_dcpr_management_activity(
        request_obj,
        activity_type=DcprManagementActivityType.DELETE_DCPR_REQUEST,
        context=context,
    )
