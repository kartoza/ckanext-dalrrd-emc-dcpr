import logging
import typing

import ckan.plugins.toolkit as toolkit

logger = logging.getLogger(__name__)


def authorize_package_publish(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    """Check if the current user as sufficient authorization to publish a dataset"""
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
