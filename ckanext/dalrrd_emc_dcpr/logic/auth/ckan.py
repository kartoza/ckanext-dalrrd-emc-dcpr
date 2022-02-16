import logging
import typing

import ckan.plugins.toolkit as toolkit

logger = logging.getLogger(__name__)


@toolkit.chained_auth_function
def package_update(next_auth, context, data_dict):
    """Custom auth for the package_update action.

    Packages that are public shall not be editable by users that are not org admins
    or site-wide sysadmins.

    """

    user = context["auth_user_obj"]
    package_show_action = toolkit.get_action("package_show")
    package = package_show_action(context, data_dict)
    if user.sysadmin:
        result = {"success": True}
    elif package.get("private"):
        result = {"success": True}
    else:
        org_id = package.get("owner_org")
        if org_id is not None:
            members_action = toolkit.get_action("member_list")
            members = members_action(data_dict={"id": org_id, "object_type": "user"})
            for member_id, _, role in members:
                if member_id == user.id and role.lower() == "admin":
                    result = {"success": True}
                    break
            else:
                org_name = package.get("organization", {}).get("name", "") or org_id
                result = {
                    "success": False,
                    "msg": (
                        f"Only administrators of organization {org_name!r} are "
                        f"authorized to edit one of its public datasets"
                    ),
                }
        else:
            result = {"success": False}
    if result["success"]:
        final_result = next_auth(context, data_dict)
    else:
        final_result = result
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
