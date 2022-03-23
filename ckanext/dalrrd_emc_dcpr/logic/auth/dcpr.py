import logging
import typing

from ckan.plugins import toolkit

logger = logging.getLogger(__name__)


def dcpr_report_create_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_report_create auth")
    user = context["auth_user_obj"]
    # Only allow creation of dcpr report if there is a user logged in.
    if user:
        return {"success": True}
    return {"success": False}


def dcpr_request_create_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_create auth")
    user = context["auth_user_obj"]
    # Only allow creation of dcpr requests if there is a user logged in.
    if user:
        return {"success": True}
    return {"success": False}


@toolkit.auth_allow_anonymous_access
def dcpr_request_list_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_list auth")
    return {"success": True}


@toolkit.auth_allow_anonymous_access
def dcpr_request_show_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_show auth")
    return {"success": True}


def dcpr_request_update_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_show auth")
    return {"success": True}
