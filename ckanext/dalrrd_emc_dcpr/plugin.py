import json
import logging
import typing
from functools import partial

from shapely import geometry

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import (
    Missing,
)  # note: imported for type hints only

from . import commands

logger = logging.getLogger(__name__)


class DalrrdEmcDcprPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("fanstatic", "dalrrd_emc_dcpr")

    def get_commands(self):
        return [
            commands.dalrrd_emc_dcpr,
        ]

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

    def get_validators(self) -> typing.Dict[str, typing.Callable]:
        return {
            "value_or_true": value_or_true_validator,
        }

    def create_package_schema(self) -> typing.Dict[str, typing.List]:
        original_schema = super().create_package_schema()
        schema = _set_schema_for_package_creation_private_field(original_schema)
        return schema

    def is_fallback(self) -> bool:
        return True

    def package_types(self) -> typing.List:
        return []

    def get_helpers(self):
        return {
            "dalrrd_emc_dcpr_default_spatial_search_extent": partial(
                get_default_spatial_search_extent, 0.001
            ),
        }


def _set_schema_for_package_creation_private_field(
    schema: typing.Dict[str, typing.List[typing.Callable]]
) -> typing.Dict[str, typing.List[typing.Callable]]:
    """Modify the validators assigned to the `private` field .

    This function modifies the `private` field's validators in order to make it
    `True` by default. The intention is that whenever a package is created, if
    a visibility is not explicitly chosen, then the package will default to being
    private.

    """

    _PRIVATE_FIELD = "private"
    private_field_validators = schema.get(_PRIVATE_FIELD, [])[:]
    # NOTE: We insert our custom validator as the first element on the list on
    # purpose.
    # The reason being that the `private` field has other validators that may
    # cause ours to be bypassed (e.g. the `ignore_missing` validator) or even
    # set a default value that is the opposite of what we want (e.g. the
    # `boolean_validator` validator)
    private_field_validators.insert(0, toolkit.get_validator("value_or_true"))
    schema.update({_PRIVATE_FIELD: private_field_validators})
    return schema


def value_or_true_validator(value: typing.Union[str, Missing]):
    """Validator that provides a default value of `True` when the input is None.

    This was designed with a package's `private` field in mind. We want it to be
    assigned a value of True when it is not explicitly provided on package creation.
    This shall enforce creating private packages by default.

    """

    logger.debug(f"inside value_or_true. Original value: {value!r}")
    return value if value != toolkit.missing else True


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
    if remains_private:
        result = action(context, data)
    else:
        access = toolkit.check_access("package_publish", context, data)
        result = action(context, data) if access else None
    return result


def get_default_spatial_search_extent(
    padding_degrees: typing.Optional[float] = None,
) -> str:
    """
    Return GeoJSON polygon with bbox to use for default view of spatial search map widget.
    """
    configured_extent = toolkit.config.get(
        "ckan.dalrrd_emc_dcpr.default_spatial_search_extent"
    )
    if padding_degrees and configured_extent:
        parsed_extent = json.loads(configured_extent)
        padded = _pad_geospatial_extent(parsed_extent, padding_degrees)
        result = json.dumps(padded)
    else:
        result = configured_extent
    return result


def _pad_geospatial_extent(extent: typing.Dict, padding: float) -> typing.Dict:
    geom = geometry.shape(extent)
    padded = geom.buffer(padding, join_style=geometry.JOIN_STYLE.mitre)
    oriented_padded = geometry.polygon.orient(padded)
    return geometry.mapping(oriented_padded)
