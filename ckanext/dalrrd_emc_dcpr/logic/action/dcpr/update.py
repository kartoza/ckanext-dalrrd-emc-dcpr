import datetime as dt
import logging
import typing

from ckan.plugins import toolkit
from sqlalchemy import exc

from ....constants import DCPRRequestStatus
from ... import schema as dcpr_schema
from ....model import dcpr_request
from .... import dcpr_dictization

logger = logging.getLogger(__name__)


def dcpr_request_update_by_owner(context, data_dict):
    schema = dcpr_schema.update_dcpr_request_by_owner_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_update_by_owner_auth", context, validated_data)
    validated_data["owner_user"] = context["auth_user_obj"].id
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    context["model"].Session.commit()
    # TODO: would be nice to add an activity here
    return dcpr_dictization.dcpr_request_dictize(request_obj, context)


def dcpr_request_update_by_nsif(context, data_dict):
    """Update a DCPR request's NSIF-related fields.

    Some fields of a DCPR request can only be modified by members of the NSIF
    organization. Additionally, once a specific user starts updating the request, it
    becomes its nsif_reviewer and all further updates by the NSIF must be done by that
    user.

    """

    schema = dcpr_schema.update_dcpr_request_by_nsif_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_update_by_nsif_auth", context, validated_data)
    validated_data.update(
        {
            "nsif_reviewer": context["auth_user_obj"].id,
            "nsif_review_date": dt.datetime.now(dt.timezone.utc),
        }
    )
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    context["model"].Session.commit()
    # TODO: would be nice to add an activity here
    return dcpr_dictization.dcpr_request_dictize(request_obj, context)


def dcpr_request_update_by_csi(context, data_dict):
    """Update a DCPR request's CSI-related fields.

    Some fields of a DCPR request can only be modified by members of the CSI
    organization. Additionally, once a specific user starts updating the request, it
    becomes its csi_moderator and all further updates by the CSI must be done by that
    user.

    """

    schema = dcpr_schema.update_dcpr_request_by_csi_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)
    toolkit.check_access("dcpr_request_update_by_csi_auth", context, validated_data)
    validated_data.update(
        {
            "csi_moderator": context["auth_user_obj"].id,
            "csi_moderation_date": dt.datetime.now(dt.timezone.utc),
        }
    )
    request_obj = dcpr_dictization.dcpr_request_dict_save(validated_data, context)
    context["model"].Session.commit()
    # TODO: would be nice to add an activity here
    return dcpr_dictization.dcpr_request_dictize(request_obj, context)


def dcpr_request_submit(context, data_dict):
    """Submit a DCPR request.

    By submitting a DCPR request, it is marked as ready for review by the SASDI
    organizations.

    """

    schema = dcpr_schema.dcpr_request_submit_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access("dcpr_request_submit_auth", context, validated_data)
    validated_data["submission_date"] = dt.datetime.now(dt.timezone.utc)
    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    if request_obj is not None:
        can_be_submitted = (
            request_obj.status == DCPRRequestStatus.UNDER_PREPARATION.value
        )
        if can_be_submitted:
            next_status = DCPRRequestStatus.AWAITING_NSIF_REVIEW.value
            request_obj.status = next_status
            model.Session.commit()
        else:
            raise RuntimeError("DCPR Request is not currently submittable")
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def dcpr_request_nsif_moderate(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    """Provide the NSIF's moderation for a DCPR request.

    By moderating a DCPR request, it is either rejected or marked as reviewed by the
    NSIF and ready for further moderation by the CSI.

    """

    schema = dcpr_schema.moderate_nsif_dcpr_request_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access("dcpr_request_nsif_moderate_auth", context, validated_data)
    validated_data["nsif_review_date"] = dt.datetime.now(dt.timezone.utc)
    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    if request_obj is not None:
        can_be_moderated = (
            request_obj.status == DCPRRequestStatus.UNDER_NSIF_REVIEW.value
        )
        if can_be_moderated:
            next_status = (
                DCPRRequestStatus.AWAITING_CSI_REVIEW.value
                if validated_data["accepted"]
                else DCPRRequestStatus.REJECTED.value
            )
            request_obj.status = next_status
            model.Session.commit()
        else:
            raise RuntimeError("DCPR Request can not currently be moderated by NSIF")
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def dcpr_request_csi_moderate(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    """Provide the CSI's moderation for a DCPR request.

    By moderating a DCPR request, it is marked as reviewed by the CSI and made public.

    """

    schema = dcpr_schema.moderate_csi_dcpr_request_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access("dcpr_request_csi_moderate_auth", context, validated_data)
    validated_data["csi_moderation_date"] = dt.datetime.now(dt.timezone.utc)
    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    if request_obj is not None:
        can_be_moderated = (
            request_obj.status == DCPRRequestStatus.UNDER_CSI_REVIEW.value
        )
        if can_be_moderated:
            final_status = (
                DCPRRequestStatus.ACCEPTED.value
                if validated_data["approved"]
                else DCPRRequestStatus.REJECTED.value
            )
            request_obj.status = final_status
            model.Session.commit()
        else:
            raise RuntimeError("DCPR Request can not currently be moderated by CSI")
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def claim_dcpr_request_nsif_reviewer(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    schema = dcpr_schema.claim_nsif_reviewer_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access(
        "dcpr_request_claim_nsif_reviewer_auth", context, validated_data
    )
    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    if request_obj is not None:
        next_status = DCPRRequestStatus.UNDER_NSIF_REVIEW.value
        request_obj.status = next_status
        model.Session.commit()
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)


def claim_dcpr_request_csi_moderator(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    schema = dcpr_schema.claim_csi_moderator_schema()
    validated_data, errors = toolkit.navl_validate(data_dict, schema, context)
    if errors:
        raise toolkit.ValidationError(errors)

    toolkit.check_access(
        "dcpr_request_claim_csi_moderator_auth", context, validated_data
    )
    model = context["model"]
    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        validated_data["csi_reference_id"]
    )
    if request_obj is not None:
        next_status = DCPRRequestStatus.UNDER_CSI_REVIEW.value
        request_obj.status = next_status
        model.Session.commit()
    else:
        raise toolkit.ObjectNotFound
    return toolkit.get_action("dcpr_request_show")(context, validated_data)
