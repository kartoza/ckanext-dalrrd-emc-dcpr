import logging
import typing

import ckan.plugins.toolkit as toolkit

logger = logging.getLogger(__name__)


@toolkit.side_effect_free
def dcpr_request_list(context: typing.Dict, data_dict: typing.Dict) -> typing.List:
    logger.debug("Inside the dcpr_request_list action")
    access_result = toolkit.check_access(
        "dcpr_request_list_auth", context, data_dict=data_dict
    )
    logger.debug(f"access_result: {access_result}")
    fake_requests = [
        {"name": "req1", "owner": "tester1"},
        {"name": "req2", "owner": "tester1"},
        {"name": "req3", "owner": "tester1"},
        {"name": "req4", "owner": "tester2"},
    ]
    result = []
    current_user = context["auth_user_obj"]
    for dcpr_request in fake_requests:
        if dcpr_request["owner"] == current_user.name:
            result.append(dcpr_request)
    return result
