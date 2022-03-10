"""Custom auth functions for ckanext-pages

These are used to control which users are allowed to edit new pages on the portal

"""

import logging
import typing

import ckan.plugins.toolkit as toolkit
from ckanext.pages import db as pages_db


logger = logging.getLogger(__name__)


@toolkit.chained_auth_function
def authorize_edit_page(
    next_auth: typing.Callable,
    context: typing.Dict,
    data_dict: typing.Optional[typing.Dict] = None,
) -> typing.Dict:
    """Check whether user should be allowed to edit pages

    This auth function customizes the default behavior of ckanext-pages. Where the
    default is to only allow sysadmins to edit a page, we instead check if they are
    members of the special portal staff group.

    As a result of this override behavior we do not call `next_auth` here - otherwise
    the default ckanext-pages auth function would be called last and it would
    end up enforcing the default behavior (i.e. only allow sysadmins to edit a page).

    """

    result = {"success": False}
    user = context["auth_user_obj"]
    if toolkit.h["emc_user_is_staff_member"](user.id):
        result["success"] = True
    else:
        result["msg"] = toolkit._("You are not authorized to edit pages")
    return result


@toolkit.chained_auth_function
def authorize_delete_page(
    next_auth: typing.Callable,
    context: typing.Dict,
    data_dict: typing.Optional[typing.Dict] = None,
) -> typing.Dict:
    """Check whether user should be allowed to delete pages

    This auth function customizes the default behavior of ckanext-pages. Where the
    default is to only allow sysadmins to delete a page, we instead check if they are
    members of the special portal staff group.

    As a result of this override behavior we do not call `next_auth` here - otherwise
    the default ckanext-pages auth function would be called last and it would
    end up enforcing the default behavior.

    """

    result = {"success": False}
    user = context["auth_user_obj"]
    if toolkit.h["emc_user_is_staff_member"](user.id):
        result["success"] = True
    else:
        result["msg"] = toolkit._("You are not authorized to delete pages")
    return result


@toolkit.chained_auth_function
@toolkit.auth_allow_anonymous_access
def authorize_show_page(
    next_auth: typing.Callable,
    context: typing.Dict,
    data_dict: typing.Optional[typing.Dict] = None,
) -> typing.Dict:
    """Check whether user should be allowed to view a page

    This auth function customized the default behavior of ckanext-pages. Where the
    default is to check if a page is public and if not only allow access to sysadmins,
    we want members of the special portal staff group to also be able to access private
    pages.

    As a result of this override behavior we may not call `next_auth` here - otherwise
    the default ckanext-pages auth function would be called last and it would
    end up enforcing the default behavior.

    """

    data_dict = dict(data_dict) if data_dict is not None else {}
    org_id = data_dict.get("org_id")
    page = data_dict.get("page")
    out = pages_db.Page.get(group_id=org_id, name=page)
    result = {"success": False}
    if out:
        if org_id:  # check membership of the user by calling original method
            result = next_auth(context, data_dict)
        else:  # universal page, lets see if page is private and/or if user is staff
            if out.private:  # user can only see it if it is from staff
                user = context["auth_user_obj"]
                if toolkit.h["emc_user_is_staff_member"](user.id):
                    result["success"] = True
                else:
                    result["msg"] = toolkit._(
                        "You are not authorized to access page %s" % page
                    )
            else:  # everyone can see it
                result["success"] = True
    else:
        result["msg"] = toolkit._("Page %s not found") % page
    return result
