import logging
import typing
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from .commands.test import test_ckan_cmd

logger = logging.getLogger(__name__)


class DalrrdEmcDcprPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("fanstatic", "dalrrd_emc_dcpr")

    def get_commands(self):
        return [test_ckan_cmd]

    # IAuthFunctions

    def get_auth_functions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_publish": authorize_package_publish,
        }

    def get_actions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_create": package_create,
            "package_update": package_update,
            "package_patch": package_patch,
        }


def authorize_package_publish(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict[str, bool]:
    # in here we can inspect the context and the data_dict in order to
    # decide whether to authorize access or not
    user_name = context.get("user")
    owner_org = data_dict.get("owner_org") or data_dict.get("group_id")

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
        logger.debug(f"Inside authorize_package_publish function: {locals()}")
        return {"success": False, "msg": "You are not authorized to publish a package"}


# IActions


@toolkit.chained_action
def package_create(original_action, context, data_dict):
    """
    Intercepts the core `package_create` action to check if package
     is being published after being created.
    """
    return package_publish_check(original_action, context, data_dict)


@toolkit.chained_action
def package_update(original_action, context, data_dict):
    """
    Intercepts the core `package_update` action to check if package is being published.
    """
    return package_publish_check(original_action, context, data_dict)


@toolkit.chained_action
def package_patch(original_action, context, data_dict):
    """
    Intercepts the core `package_patch` action to check if package is being published.
    """
    return package_publish_check(original_action, context, data_dict)


def package_publish_check(action, context, data):
    remains_private = toolkit.asbool(data.get("private", True))
    result = None
    if remains_private:
        # make sure private state is updated, then assign result
        data.update({"private": remains_private})
        result = action(context, data)
    else:
        toolkit.check_access("package_publish", context, data)
    return result
