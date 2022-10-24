import typing

from ckan.logic.schema import default_create_activity_schema
from ckan.plugins import toolkit

from ...constants import (
    DatasetManagementActivityType,
    DcprManagementActivityType,
)
from ...dcpr_dictization import dcpr_request_dictize
from ...model.dcpr_request import DCPRRequest


def create_dataset_management_activity(
    dataset_id: str, activity_type: DatasetManagementActivityType
) -> typing.Dict:
    """
    This is a hacky way to relax the activity type schema validation
    we remove the default activity_type_exists validator because it is not possible
    to extend it with a custom activity
    """

    activity_schema = default_create_activity_schema()
    to_remove = None
    for index, validator in enumerate(activity_schema["activity_type"]):
        if validator.__name__ == "activity_type_exists":
            to_remove = validator
            break
    if to_remove:
        activity_schema["activity_type"].remove(to_remove)
    to_remove = None
    for index, validator in enumerate(activity_schema["object_id"]):
        if validator.__name__ == "object_id_validator":
            to_remove = validator
            break
    if to_remove:
        activity_schema["object_id"].remove(to_remove)
    activity_schema["object_id"].append(toolkit.get_validator("package_id_exists"))
    dataset = toolkit.get_action("package_show")(data_dict={"id": dataset_id})
    return toolkit.get_action("activity_create")(
        context={
            "ignore_auth": True,
            "schema": activity_schema,
        },
        data_dict={
            "user_id": toolkit.g.userobj.id,
            "object_id": dataset_id,
            "activity_type": activity_type.value,
            "data": {
                "package": dataset,
            },
        },
    )


def create_dcpr_management_activity(
    dcpr_request_obj: DCPRRequest,
    activity_type: DcprManagementActivityType,
    context: typing.Dict,
) -> typing.Dict:
    """
    This is a hacky way to relax the activity type schema validation
    we remove the default activity_type_exists validator because it is not possible
    to extend it with a custom activity
    """

    activity_schema = default_create_activity_schema()
    to_remove = None
    for index, validator in enumerate(activity_schema["activity_type"]):
        if validator.__name__ == "activity_type_exists":
            to_remove = validator
            break
    if to_remove:
        activity_schema["activity_type"].remove(to_remove)
    to_remove = None
    for index, validator in enumerate(activity_schema["object_id"]):
        if validator.__name__ == "object_id_validator":
            to_remove = validator
            break
    if to_remove:
        activity_schema["object_id"].remove(to_remove)
    action_context = context.copy()
    action_context.update(
        {
            "ignore_auth": True,
            "schema": activity_schema,
        }
    )
    user_id = {
        DcprManagementActivityType.CREATE_DCPR_REQUEST: dcpr_request_obj.owner_user,
        DcprManagementActivityType.UPDATE_DCPR_REQUEST_BY_OWNER: dcpr_request_obj.owner_user,
        DcprManagementActivityType.SUBMIT_DCPR_REQUEST: dcpr_request_obj.owner_user,
        DcprManagementActivityType.DELETE_DCPR_REQUEST: dcpr_request_obj.owner_user,
        DcprManagementActivityType.BECOME_NSIF_REVIEWER_DCPR_REQUEST: dcpr_request_obj.nsif_reviewer,
        DcprManagementActivityType.RESIGN_NSIF_REVIEWER_DCPR_REQUEST: dcpr_request_obj.nsif_reviewer,
        DcprManagementActivityType.UPDATE_DCPR_REQUEST_BY_NSIF: dcpr_request_obj.nsif_reviewer,
        DcprManagementActivityType.ACCEPT_DCPR_REQUEST_NSIF: dcpr_request_obj.nsif_reviewer,
        DcprManagementActivityType.REJECT_DCPR_REQUEST_NSIF: dcpr_request_obj.nsif_reviewer,
        DcprManagementActivityType.REQUEST_CLARIFICATION_DCPR_REQUEST_NSIF: dcpr_request_obj.nsif_reviewer,
        DcprManagementActivityType.BECOME_CSI_REVIEWER_DCPR_REQUEST: dcpr_request_obj.csi_moderator,
        DcprManagementActivityType.RESIGN_CSI_REVIEWER_DCPR_REQUEST: dcpr_request_obj.csi_moderator,
        DcprManagementActivityType.UPDATE_DCPR_REQUEST_BY_CSI: dcpr_request_obj.csi_moderator,
        DcprManagementActivityType.ACCEPT_DCPR_REQUEST_CSI: dcpr_request_obj.csi_moderator,
        DcprManagementActivityType.REJECT_DCPR_REQUEST_CSI: dcpr_request_obj.csi_moderator,
        DcprManagementActivityType.REQUEST_CLARIFICATION_DCPR_REQUEST_CSI: dcpr_request_obj.csi_moderator,
    }.get(activity_type)

    return toolkit.get_action("activity_create")(
        context=action_context,
        data_dict={
            "user_id": user_id,
            "object_id": dcpr_request_obj.csi_reference_id,
            "activity_type": activity_type.value,
            "data": {
                "dcpr_request": dcpr_request_dictize(dcpr_request_obj, context),
            },
        },
    )
