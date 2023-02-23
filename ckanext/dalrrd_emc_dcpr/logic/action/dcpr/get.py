import logging
import typing

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
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_show_auth", context, validated_data)
    request_object = dcpr_request.DCPRRequest.get(validated_data["csi_reference_id"])
    if not request_object:
        raise toolkit.ObjectNotFound
    return dcpr_dictization.dcpr_request_dictize(request_object, context)


@toolkit.side_effect_free
def dcpr_request_list_public(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of public DCPR requests."""
    toolkit.check_access("dcpr_request_list_public_auth", context, data_dict or {})
    relevant_statuses = (
        DCPRRequestStatus.ACCEPTED.value,
        DCPRRequestStatus.REJECTED.value,
    )
    return _get_dcpr_request_list(
        context,
        data_dict,
        filter_=dcpr_request.DCPRRequest.status.in_(relevant_statuses),
    )


@toolkit.side_effect_free
def my_dcpr_request_list(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.List[typing.Dict]:
    toolkit.check_access("my_dcpr_request_list_auth", context, data_dict or {})
    return _get_dcpr_request_list(
        context,
        data_dict,
        filter_=dcpr_request.DCPRRequest.owner_user == context["auth_user_obj"].id,
    )


@toolkit.side_effect_free
def dcpr_request_list_under_preparation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List[typing.Dict]:
    """Return a list of DCPR requests that are still being prepared.

    This function returns all DCPR requests that are being prepared by all users.

    """

    toolkit.check_access(
        "dcpr_request_list_under_preparation_auth", context, data_dict or {}
    )
    return _get_dcpr_request_list(
        context,
        data_dict,
        filter_=dcpr_request.DCPRRequest.status
        == DCPRRequestStatus.UNDER_PREPARATION.value,
    )


@toolkit.side_effect_free
def dcpr_request_list_awaiting_csi_moderation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of DCPR requests that are awaiting moderation by CSI members."""
    # mohab: we are adding request_origin
    # so the check is not applied when it
    # comes from /dataset/ page.
    try:
        request_origin = context["request_origin"]
    except KeyError:
        request_origin = ""
    if "/dataset/" not in request_origin:
        toolkit.check_access(
            "dcpr_request_list_pending_csi_auth", context, data_dict or {}
        )
    relevant_statuses = (
        DCPRRequestStatus.AWAITING_CSI_REVIEW.value,
        DCPRRequestStatus.UNDER_CSI_REVIEW.value,
    )
    return _get_dcpr_request_list(
        context,
        data_dict,
        filter_=dcpr_request.DCPRRequest.status.in_(relevant_statuses),
    )


@toolkit.side_effect_free
def dcpr_request_list_awaiting_nsif_moderation(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.List:
    """Return a list of DCPR requests that are awaiting moderation by NSIF members."""
    toolkit.check_access(
        "dcpr_request_list_pending_nsif_auth", context, data_dict or {}
    )
    relevant_statuses = (
        DCPRRequestStatus.AWAITING_NSIF_REVIEW.value,
        DCPRRequestStatus.UNDER_NSIF_REVIEW.value,
    )
    return _get_dcpr_request_list(
        context,
        data_dict,
        filter_=dcpr_request.DCPRRequest.status.in_(relevant_statuses),
    )


def _get_dcpr_request_list(
    context: typing.Dict,
    data_dict: typing.Optional[typing.Dict] = None,
    filter_=None,
) -> typing.List[typing.Dict]:
    data_ = data_dict if data_dict is not None else {}
    query = context["model"].Session.query(dcpr_request.DCPRRequest)
    if filter_ is not None:
        query = query.filter(filter_)
    query = (
        query.order_by(
            # dcpr_request.DCPRRequest.status,
            dcpr_request.DCPRRequest.submission_date.desc(),
            dcpr_request.DCPRRequest.nsif_review_date,
            dcpr_request.DCPRRequest.csi_moderation_date,
            dcpr_request.DCPRRequest.proposed_project_name,
        )
        # .limit(data_.get("limit", 10))
        # .offset(data_.get("offset", 0))
    )
    return [dcpr_dictization.dcpr_request_dictize(i, context) for i in query.all()]
