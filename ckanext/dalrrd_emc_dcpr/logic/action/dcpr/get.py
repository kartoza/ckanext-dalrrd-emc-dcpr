import logging
import typing

import ckan.lib.dictization as d
from ckan.plugins import toolkit

from ....model import dcpr_request
from .... import dcpr_dictization

logger = logging.getLogger(__name__)


# TODO: sort the list by recently modified
@toolkit.side_effect_free
def dcpr_request_list_public(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of public DCPR requests."""
    toolkit.check_access(
        "dcpr_request_list_public_auth", context, data_dict=data_dict or {}
    )
    query = (
        context["model"]
        .Session.query(dcpr_request.DCPRRequest)
        .limit(data_dict.get("limit", 10))
        .offset(data_dict.get("offset", 0))
    )
    result = [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]
    logger.info(f"{result=}")
    return result


@toolkit.side_effect_free
def dcpr_request_list_private(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of private DCPR requests"""
    raise NotImplementedError


@toolkit.side_effect_free
def dcpr_request_list_awaiting_csi_moderation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of DCPR requests that are awaiting moderation by CSI members."""
    raise NotImplementedError


@toolkit.side_effect_free
def dcpr_request_list_awaiting_nsif_moderation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of DCPR requests that are awaiting moderation by NSIF members."""
    raise NotImplementedError


@toolkit.side_effect_free
def dcpr_request_show(context: typing.Dict, data_dict: typing.Dict) -> typing.List:
    request_id = toolkit.get_or_bust(data_dict, "id")

    request_object = dcpr_request.DCPRRequest.get(csi_reference_id=request_id)

    if not request_object:
        raise toolkit.ObjectNotFound

    toolkit.check_access("dcpr_request_show_auth", context, data_dict)

    request_dict = d.table_dictize(request_object, context)

    return request_dict
