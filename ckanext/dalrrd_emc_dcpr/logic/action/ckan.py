"""Override of CKAN actions"""

import logging

import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

from ckanext.dalrrd_emc_dcpr.model.request import Request

logger = logging.getLogger(__name__)

_get_or_bust = logic.get_or_bust
ValidationError = toolkit.ValidationError


@toolkit.chained_action
def package_create(original_action, context, data_dict):
    """
    Intercepts the core `package_create` action to check if package
     is being published after being created.
    """
    return _package_publish_check(original_action, context, data_dict)


@toolkit.chained_action
def package_update(original_action, context, data_dict):
    """
    Intercepts the core `package_update` action to check if package is being published.
    """
    return _package_publish_check(original_action, context, data_dict)


@toolkit.chained_action
def package_patch(original_action, context, data_dict):
    """
    Intercepts the core `package_patch` action to check if package is being published.
    """
    return _package_publish_check(original_action, context, data_dict)


def request_create(context, data_dict):
    model = context["model"]
    _request_check_access("request_create", context, data_dict)

    csi_reference_id = data_dict["csi_reference_id"]

    request = (
        model.Session.query(Request)
        .filter(Request.csi_reference_id == csi_reference_id)
        .first()
    )

    if request:
        raise ValidationError({"message": "Request already exists"})
    else:
        request = Request(
            csi_reference_id=data_dict.csi_reference_id,
            status=data_dict.status,
            organization_name=data_dict.organization_name,
            organization_level=data_dict.organization_level,
            organization_address=data_dict.organization_address,
            proposed_project_name=data_dict.proposed_project_name,
            additional_project_context=data_dict.additional_project_context,
            capture_start_date=data_dict.capture_start_date,
            capture_end_date=data_dict.capture_end_date,
            request_dataset=data_dict.request_dataset,
            cost=data_dict.cost,
            spatial_extent=data_dict.spatial_extent,
            spatial_resolution=data_dict.spatial_resolution,
            data_capture_urgency=data_dict.data_capture_urgency,
            additional_information=data_dict.additional_information,
            request_date=data_dict.data_dict_date,
            submission_date=data_dict.submission_date,
        )

    model.Session.add(request)
    model.repo.commit()

    return request


def _request_check_access(action, context, data):
    access = toolkit.check_access("request_create", context, data)
    result = action(context, data) if access else None
    return result


def _package_publish_check(action, context, data):
    remains_private = toolkit.asbool(data.get("private", True))
    if remains_private:
        result = action(context, data)
    else:
        access = toolkit.check_access("package_publish", context, data)
        result = action(context, data) if access else None
    return result
