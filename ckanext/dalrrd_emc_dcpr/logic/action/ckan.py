"""Override of CKAN actions"""

import logging
import typing

import ckan.plugins.toolkit as toolkit

logger = logging.getLogger(__name__)


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
    logger.debug(f"inside package_update action: {data_dict=}")
    return _package_publish_check(original_action, context, data_dict)


@toolkit.chained_action
def package_patch(original_action, context, data_dict):
    """
    Intercepts the core `package_patch` action to check if package is being published.
    """
    return _package_publish_check(original_action, context, data_dict)


def user_patch(context: typing.Dict, data_dict: typing.Dict) -> typing.Dict:
    """Implements user_patch action, which is not available on CKAN

    The `data_dict` parameter is expected to contain at least the `id` key, which
    should hold the user's id or name

    """

    logger.debug(f"{locals()=}")
    logger.debug("About to check access of user_update")
    toolkit.check_access("user_update", context, data_dict)
    logger.debug("After checking access of user_update")
    show_context = {
        "model": context["model"],
        "session": context["session"],
        "user": context["user"],
        "auth_user_obj": context["auth_user_obj"],
    }
    user_dict = toolkit.get_action("user_show")(
        show_context, data_dict={"id": context["user"]}
    )
    logger.debug(f"{user_dict=}")
    patched = dict(user_dict)
    patched.update(data_dict)
    logger.debug(f"{patched=}")
    update_action = toolkit.get_action("user_update")
    return update_action(context, patched)


def _package_publish_check(action, context, data):
    remains_private = toolkit.asbool(data.get("private", True))
    if remains_private:
        result = action(context, data)
    else:
        access = toolkit.check_access("package_publish", context, data)
        result = action(context, data) if access else None
    return result
