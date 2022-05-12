import logging
import typing

import ckan.lib.dictization as d
from ckan.plugins import toolkit

from ....model import dcpr_request
from .... import dcpr_dictization
from ....constants import DCPRRequestStatus
from ...schema import show_dcpr_request_schema

logger = logging.getLogger(__name__)


@toolkit.side_effect_free
def dcpr_request_show(context: typing.Dict, data_dict: typing.Dict) -> typing.Dict:
    schema = show_dcpr_request_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    model = context["model"]
    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_show_auth", context, validated_data)
    request_object = dcpr_request.DCPRRequest.get(validated_data["csi_reference_id"])
    if not request_object:
        raise toolkit.ObjectNotFound
    return dcpr_dictization.dcpr_request_dictize(request_object, context)


# TODO: sort the list by recently modified
@toolkit.side_effect_free
def dcpr_request_list_public(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of public DCPR requests."""
    toolkit.check_access("dcpr_request_list_public_auth", context, data_dict)
    public_statuses = (
        DCPRRequestStatus.ACCEPTED.value,
        DCPRRequestStatus.REJECTED.value,
    )
    query = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .filter(dcpr_request.DCPRRequest.status.in_(public_statuses))
        .limit(data_dict.get("limit", 10))
        .offset(data_dict.get("offset", 0))
    )
    return [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]


@toolkit.side_effect_free
def my_dcpr_request_list(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List[typing.Dict]:
    toolkit.check_access("my_dcpr_request_list_auth", context, data_dict)
    query = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .filter(dcpr_request.DCPRRequest.owner_user == context["auth_user_obj"].id)
        .limit(data_dict.get("limit", 10))
        .offset(data_dict.get("offset", 0))
    )
    return [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]


@toolkit.side_effect_free
def dcpr_request_list_private(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List[typing.Dict]:
    """Return a list of private DCPR requests"""
    toolkit.check_access("dcpr_request_list_private_auth", context, data_dict)
    query = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .filter(
            dcpr_request.DCPRRequest.status == DCPRRequestStatus.UNDER_PREPARATION.value
        )
        .limit(data_dict.get("limit", 10))
        .offset(data_dict.get("offset", 0))
    )
    return [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]


@toolkit.side_effect_free
def dcpr_request_list_awaiting_csi_moderation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of DCPR requests that are awaiting moderation by CSI members."""
    toolkit.check_access("dcpr_request_list_pending_csi_auth", context, data_dict)
    csi_statuses = (
        DCPRRequestStatus.AWAITING_CSI_REVIEW.value,
        DCPRRequestStatus.UNDER_CSI_REVIEW.value,
    )
    query = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .filter(dcpr_request.DCPRRequest.status.in_(csi_statuses))
        .limit(data_dict.get("limit", 10))
        .offset(data_dict.get("offset", 0))
    )
    return [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]


@toolkit.side_effect_free
def dcpr_request_list_awaiting_nsif_moderation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of DCPR requests that are awaiting moderation by NSIF members."""
    toolkit.check_access("dcpr_request_list_pending_nsif_auth", context, data_dict)
    nsif_statuses = (
        DCPRRequestStatus.AWAITING_NSIF_REVIEW.value,
        DCPRRequestStatus.UNDER_NSIF_REVIEW.value,
    )
    query = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .filter(dcpr_request.DCPRRequest.status.in_(nsif_statuses))
        .limit(data_dict.get("limit", 10))
        .offset(data_dict.get("offset", 0))
    )
    return [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]
