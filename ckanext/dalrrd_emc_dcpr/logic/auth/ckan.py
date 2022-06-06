import logging
import typing

import ckan.plugins.toolkit as toolkit
from ckan.logic.auth import get_package_object

from ckanext.harvest.utils import DATASET_TYPE_NAME as CKANEXT_HARVEST_DATASET_TYPE_NAME

logger = logging.getLogger(__name__)


@toolkit.chained_auth_function
def package_update(next_auth, context, data_dict=None):
    """Custom auth for the package_update action.

    Packages that are public shall not be editable by users that are not org admins
    or site-wide sysadmins.

    """

    user = context["auth_user_obj"]
    if user.sysadmin:
        final_result = next_auth(context, data_dict)
    elif data_dict is not None:
        # NOTE: we do not call toolkit.get_action("package_show") here but rather do it
        # the same as vanilla CKAN which uses a custom way to retrieve the object from
        # the context - this is in order to ensure other extensions
        # (e.g. ckanext.harvest) are able to function correctly
        package = get_package_object(context, data_dict)
        if package.type == CKANEXT_HARVEST_DATASET_TYPE_NAME:
            # defer auth to the ckanext.harvest extension
            final_result = next_auth(context, data_dict)
        else:
            result = {"success": False}
            if package.private or package.state == "draft":
                result["success"] = True
            else:
                org_id = data_dict.get("owner_org", package.owner_org)
                if org_id is not None:
                    members = toolkit.get_action("member_list")(
                        data_dict={"id": org_id, "object_type": "user"}
                    )
                    for member_id, _, role in members:
                        if member_id == user.id and role.lower() == "admin":
                            result["success"] = True
                            break
                    else:
                        result["msg"] = (
                            f"Only administrators of organization {org_id!r} are "
                            f"authorized to edit one of its public datasets"
                        )
            if result["success"]:
                final_result = next_auth(context, data_dict)
            else:
                final_result = result
    else:
        final_result = next_auth(context, data_dict)
    return final_result


@toolkit.chained_auth_function
def package_patch(
    next_auth: typing.Callable, context: typing.Dict, data_dict: typing.Dict
):
    """Custom auth for the package_patch action."""
    logger.debug("inside custom package_patch auth")
    return package_update(next_auth, context, data_dict)


def authorize_package_publish(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    """Check if the current user is authorized to publish a dataset

    Only org admins or site-wide sysadmins are authorized to publish a dataset (i.e.
    make it public).

    """

    data_ = data_dict.copy() if data_dict else {}
    user = context["auth_user_obj"]
    result = {"success": False, "msg": "You are not authorized to publish package"}
    # TODO: check whether we need to make this check, as sysadmin is likely granted access by default
    if user.sysadmin:
        result = {"success": True}
    else:
        # if we have an org to check we can check if package can be published, otherwise
        # we have no way of knowing if the user is a member of the target org
        # beforehand, so we deny
        owner_org = data_.get("owner_org", data_.get("group_id"))
        if owner_org is not None:
            members = toolkit.get_action("member_list")(
                data_dict={"id": owner_org, "object_type": "user"}
            )
            admin_member_ids = [
                member_tuple[0]
                for member_tuple in members
                if member_tuple[2] == "Admin"
            ]
            if user.id in admin_member_ids:
                result = {"success": True}
    return result
