import logging
import typing

from ckan.plugins import toolkit

logger = logging.getLogger(__name__)


def authorize_list_featured_datasets(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict]
) -> typing.Dict:
    return {"success": True}


def authorize_request_dataset_maintenance(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    """Checks if current user is an editor of the same org where dataset belongs."""
    dataset = toolkit.get_action("package_show")(
        data_dict={"id": data_dict.get("pkg_id")}
    )
    is_editor = toolkit.h["emc_user_is_org_member"](
        dataset["owner_org"], context["auth_user_obj"], role="editor"
    )
    result = {"success": False}
    if is_editor:
        result["success"] = True
    return result
