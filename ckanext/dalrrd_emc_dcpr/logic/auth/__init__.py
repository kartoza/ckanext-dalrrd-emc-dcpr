import typing

import ckan.plugins.toolkit as toolkit


def authorize_package_publish(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict[str, bool]:
    user_name = context.get("user")
    owner_org = data_dict.get("owner_org")

    members = toolkit.get_action("member_list")(
        data_dict={"id": owner_org, "object_type": "user"}
    )
    admin_member_ids = [
        member_tuple[0] for member_tuple in members if member_tuple[2] == "Admin"
    ]
    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = convert_user_name_or_id_to_id(user_name, context)

    if user_id in admin_member_ids:
        return {"success": True}
    else:
        return {"success": False, "msg": "You are not authorized to publish a package"}
