import logging
import typing

from ckan.plugins import toolkit

logger = logging.getLogger(__name__)


def dcpr_request_create_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_create auth")
    user = context["auth_user_obj"]
    if user.sysadmin:
        return {"success": True}
    return {"success": False}


@toolkit.auth_allow_anonymous_access
def dcpr_request_list_auth(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict] = None
) -> typing.Dict:
    logger.debug("Inside the dcpr_request_list auth")
    return {"success": True}
