import json
import logging
import typing
from functools import partial

from flask import Blueprint
from shapely import geometry

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import (
    Missing,
)  # note: imported for type hints only

from . import (
    blueprint,
    commands,
)
from .constants import SASDI_THEMES_VOCABULARY_NAME
from .logic.action import ckan as ckan_actions
from .logic.action import dcpr as dcpr_actions
from .logic import auth
from .logic.auth import dcpr as dcpr_auth

logger = logging.getLogger(__name__)


class DalrrdEmcDcprPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IFacets)

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
            "package_publish": auth.authorize_package_publish,
            "dcpr_request_list_auth": dcpr_auth.dcpr_request_list_auth,
        }

    def get_actions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_create": ckan_actions.package_create,
            "package_update": ckan_actions.package_update,
            "package_patch": ckan_actions.package_patch,
            "dcpr_request_list": dcpr_actions.dcpr_request_list,
        }

    def get_validators(self) -> typing.Dict[str, typing.Callable]:
        return {
            "value_or_true": value_or_true_validator,
        }

    def create_package_schema(self) -> typing.Dict[str, typing.List[typing.Callable]]:
        original_schema = super().create_package_schema()
        schema = _modify_package_schema(original_schema)
        schema = _set_schema_for_package_creation_private_field(schema)
        return schema

    def update_package_schema(self) -> typing.Dict[str, typing.List[typing.Callable]]:
        original_schema = super().update_package_schema()
        schema = _modify_package_schema(original_schema)
        return schema

    def show_package_schema(self) -> typing.Dict[str, typing.List[typing.Callable]]:
        schema = super().show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema["tags"]["__extras"].append(toolkit.get_converter("free_tags_only"))

        # Add our custom sasdi_theme metadata field to the schema.
        schema.update(
            {
                "sasdi_theme": [
                    toolkit.get_converter("convert_from_tags")(
                        SASDI_THEMES_VOCABULARY_NAME
                    ),
                    toolkit.get_validator("ignore_missing"),
                ]
            }
        )
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
            "sasdi_themes": get_sasdi_themes,
        }

    def get_blueprint(self) -> typing.List[Blueprint]:
        return [
            blueprint.dcpr_blueprint,
        ]

    def dataset_facets(
        self, facets_dict: typing.OrderedDict, package_type: str
    ) -> typing.OrderedDict:
        facets_dict[f"vocab_{SASDI_THEMES_VOCABULARY_NAME}"] = toolkit._("SASDI theme")
        return facets_dict

    def group_facets(
        self, facets_dict: typing.OrderedDict, group_type: str, package_type: str
    ) -> typing.OrderedDict:
        """IFacets interface requires reimplementation of all facets-related methods

        In this case we do not really need to override this method, but need to satisfy
        IFacets.

        """

        return facets_dict


def get_sasdi_themes() -> typing.List:
    try:
        sasdi_themes = toolkit.get_action("tag_list")(
            data_dict={"vocabulary_id": SASDI_THEMES_VOCABULARY_NAME}
        )
    except toolkit.ObjectNotFound:
        sasdi_themes = []
    return sasdi_themes


def _modify_package_schema(
    schema: typing.Dict[str, typing.List[typing.Callable]]
) -> typing.Dict[str, typing.List[typing.Callable]]:
    schema["sasdi_theme"] = [
        toolkit.get_validator("ignore_missing"),
        toolkit.get_converter("convert_to_tags")(SASDI_THEMES_VOCABULARY_NAME),
    ]
    return schema


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
