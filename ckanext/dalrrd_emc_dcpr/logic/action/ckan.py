"""Override of CKAN actions"""

import logging
import typing

import ckan.plugins.toolkit as toolkit
from ckan.model.domain_object import DomainObject

from ...model.user_extra_fields import UserExtraFields
from .dataset_versioning_control import handle_versioning
from .handle_repeating_subfields import handle_repeating_subfields_naming
from .add_named_url import handle_named_url
import ckan.logic as logic
import ckan.plugins as plugins
import ckan.lib.navl.dictization_functions
import ckan.lib.uploader as uploader
import ckan.lib.dictization.model_save as model_save
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.logic.schema as schema_
from mimetypes import MimeTypes

import datetime

_validate = ckan.lib.navl.dictization_functions.validate
logger = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust
_get_action = logic.get_action
_check_access = logic.check_access
ValidationError = logic.ValidationError
NotFound = logic.NotFound

mimeNotAllowed = [
    "text/html", 
    "application/java", 
    "application/java-byte-code", 
    "application/x-javascript", 
    "application/javascript", 
    "application/ecmascript", 
    "text/javascript", 
    "text/ecmascript",
    "application/octet-stream",
    "text/x-server-parsed-html",
    "text/x-server-parsed-html"
]

@toolkit.chained_action
def resource_create(original_action, context: dict, data_dict: dict) -> dict:
    '''Appends a new resource to a datasets list of resources.

    :param package_id: id of package that the resource should be added to.

    :type package_id: string
    :param url: url of resource
    :type url: string
    :param description: (optional)
    :type description: string
    :param format: (optional)
    :type format: string
    :param hash: (optional)
    :type hash: string
    :param name: (optional)
    :type name: string
    :param resource_type: (optional)
    :type resource_type: string
    :param mimetype: (optional)
    :type mimetype: string
    :param mimetype_inner: (optional)
    :type mimetype_inner: string
    :param cache_url: (optional)
    :type cache_url: string
    :param size: (optional)
    :type size: int
    :param created: (optional)
    :type created: iso date string
    :param last_modified: (optional)
    :type last_modified: iso date string
    :param cache_last_updated: (optional)
    :type cache_last_updated: iso date string
    :param upload: (optional)
    :type upload: FieldStorage (optional) needs multipart/form-data

    :returns: the newly created resource
    :rtype: dictionary

    '''

    logger.debug(f"CALLED FROM RESOURCE CREATE")

    model = context['model']
    user = context['user']

    package_id = _get_or_bust(data_dict, 'package_id')
    if not data_dict.get('url'):
        data_dict['url'] = ''

    pkg_dict = _get_action('package_show')(
        dict(context, return_type='dict'),
        {'id': package_id})

    _check_access('resource_create', context, data_dict)

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_create(context, data_dict)

    if 'resources' not in pkg_dict:
        pkg_dict['resources'] = []

    upload = uploader.get_resource_uploader(data_dict)

    if 'mimetype' not in data_dict:
        if hasattr(upload, 'mimetype'):
            data_dict['mimetype'] = upload.mimetype

    if upload.mimetype in mimeNotAllowed:
        raise ValidationError([f"Mimetype {upload.mimetype} is not allowed!"])

    if 'size' not in data_dict:
        if hasattr(upload, 'filesize'):
            data_dict['size'] = upload.filesize

    pkg_dict['resources'].append(data_dict)

    try:
        context['defer_commit'] = True
        context['use_cache'] = False
        _get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')
    except ValidationError as e:
        try:
            raise ValidationError(e.error_dict['resources'][-1])
        except (KeyError, IndexError):
            raise ValidationError(e.error_dict)

    # Get out resource_id resource from model as it will not appear in
    # package_show until after commit
    upload.upload(context['package'].resources[-1].id,
                  uploader.get_max_resource_size())

    model.repo.commit()

    #  Run package show again to get out actual last_resource
    updated_pkg_dict = _get_action('package_show')(context, {'id': package_id})
    resource = updated_pkg_dict['resources'][-1]

    #  Add the default views to the new resource
    logic.get_action('resource_create_default_resource_views')(
        {'model': context['model'],
         'user': context['user'],
         'ignore_auth': True
         },
        {'resource': resource,
         'package': updated_pkg_dict
         })

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_create(context, resource)

    return resource

@toolkit.chained_action
def user_show(original_action, context, data_dict):
    """
    Intercepts the core `user_show` action to add any extra_fields that may exist for
    the user
    """

    original_result = original_action(context, data_dict)
    user_id = original_result.get("id")
    model = context["model"]
    user_obj = model.Session.query(model.User).filter_by(id=user_id).first()
    if user_obj.extra_fields is not None:
        original_result["extra_fields"] = _dictize_user_extra_fields(
            user_obj.extra_fields
        )
    else:
        original_result["extra_fields"] = None
    return original_result


@toolkit.chained_action
def user_update(original_action, context, data_dict):
    """
    Intercepts the core `user_update` action to update any extra_fields that may exist
    for the user.

    """
    original_result = original_action(context, data_dict)

    mime = MimeTypes()
    mime_type = mime.guess_type(original_result["image_url"])

    logger.debug(f"mime_type update{mime_type}")
    
    if mime_type[0] in mimeNotAllowed:
        raise ValidationError([f"Mimetype {mime_type} is not allowed!"])

    user_id = original_result["id"]
    model = context["model"]
    user_obj = model.Session.query(model.User).filter_by(id=user_id).first()
    if user_obj.extra_fields is None:
        extra = UserExtraFields(user_id=user_id)
    else:
        extra = user_obj.extra_fields
    extra.affiliation = data_dict.get("extra_fields_affiliation")
    extra.professional_occupation = data_dict.get(
        "extra_fields_professional_occupation"
    )
    model.Session.add(extra)
    model.Session.commit()
    logger.debug(f"{original_result=}")
    original_result["extra_fields"] = _dictize_user_extra_fields(extra)
    return original_result


@toolkit.chained_action
def user_create(original_action, context, data_dict):
    """Intercepts the core `user_create` action to also create the extra_fields."""
    original_result = original_action(context, data_dict)
    logger.debug(f"user create {original_action}")
    # mime = MimeTypes()
    # mime_type = mime.guess_type(original_result["image_url"])

    # logger.debug(f"mime_type update{mime_type}")
    
    # if mime_type[0] in mimeNotAllowed:
    #     raise ValidationError([f"Mimetype {mime_type} is not allowed!"])
    user_id = original_result["id"]
    model = context["model"]
    extra = UserExtraFields(
        user_id=user_id,
        affiliation=data_dict.get("extra_fields") or "",
        professional_occupation=data_dict.get("extra_fields") or "",
    )
    model.Session.add(extra)
    model.Session.commit()
    original_result["extra_fields"] = _dictize_user_extra_fields(extra)
    return original_result


def _dictize_user_extra_fields(user_extra_fields: UserExtraFields) -> typing.Dict:
    dictized_extra = DomainObject.as_dict(user_extra_fields)
    del dictized_extra["id"]
    del dictized_extra["user_id"]
    return dictized_extra

@toolkit.chained_action
def organization_create(original_action, context, data_dict):
    original_result = original_action(context, data_dict)
    # mime = MimeTypes()
    # mime_type = mime.guess_type(original_result["image_url"])

    # logger.debug(f"mime_type update{mime_type}")
    
    # if mime_type[0] in mimeNotAllowed:
    #     raise ValidationError([f"Mimetype {mime_type} is not allowed!"])
    return original_result

@toolkit.chained_action
def organization_update(original_action, context, data_dict):
    original_result = original_action(context, data_dict)
    mime = MimeTypes()
    mime_type = mime.guess_type(original_result["image_url"])

    logger.debug(f"mime_type update{mime_type}")
    
    if mime_type[0] in mimeNotAllowed:
        raise ValidationError([f"Mimetype {mime_type} is not allowed!"])
    return original_result

@toolkit.chained_action
def package_create(original_action, context, data_dict):
    """
    Intercepts the core `package_create` action to check if package
     is being published after being created.
    """
    named_url = handle_named_url(data_dict)
    data_dict["name"] = named_url
    return _act_depending_on_package_visibility(original_action, context, data_dict)


@toolkit.chained_action
def package_update(original_action, context, data_dict):
    """
    Intercepts the core `package_update` action to check if package is being published.
    """
    logger.debug(f"inside package_update action: {data_dict=}")
    package_state = data_dict.get("state")
    # if package_state == "draft":
    #     return _act_depending_on_package_visibility(original_action, context, data_dict)
    # else:
    #     handle_versioning(context, data_dict)
    return _act_depending_on_package_visibility(original_action, context, data_dict)


@toolkit.chained_action
def package_patch(original_action, context, data_dict):
    """
    Intercepts the core `package_patch` action to check if package is being published.
    """
    return _act_depending_on_package_visibility(original_action, context, data_dict)


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


def _act_depending_on_package_visibility(
    action: typing.Callable, context: typing.Dict, data: typing.Dict
):
    remains_private = toolkit.asbool(data.get("private", True))
    if remains_private:
        result = action(context, data)
    else:
        access = toolkit.check_access("package_publish", context, data)
        result = action(context, data) if access else None
        # if you create, update or patch you are following the dataset
        # this make a failure when the dataset is changed from private to public:
        # message form contains invalid entries: Y (maybe because the user already follow ? )
        # if access:
        #     toolkit.get_action("follow_dataset")(context, result)

    return result
