"""Override of CKAN actions"""

import logging

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


def _package_publish_check(action, context, data):
    remains_private = toolkit.asbool(data.get("private", True))
    if remains_private:
        result = action(context, data)
    else:
        access = toolkit.check_access("package_publish", context, data)
        result = action(context, data) if access else None
    return result
