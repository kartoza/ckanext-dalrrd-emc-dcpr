import logging
import typing
from functools import partial

from flask import Blueprint

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from . import (
    blueprint,
    constants,
    helpers,
)
from .cli import commands
from .logic.action import ckan as ckan_actions
from .logic.action import dcpr as dcpr_actions
from .logic import (
    auth,
    converters,
    validators,
)
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
            "value_or_true": validators.emc_value_or_true_validator,
            "emc_convert_to_tags": converters.emc_convert_to_tags,
            "emc_convert_from_tags": converters.emc_convert_from_tags,
        }

    # FIXME: because we are saying that packages of type 'dataset' are handled by ckanext-scheming, this method is not read at all
    # def create_package_schema(self) -> typing.Dict[str, typing.List[typing.Callable]]:
    #     original_schema = super().create_package_schema()
    #     schema = _modify_package_schema(original_schema)
    #     schema = _set_schema_for_package_creation_private_field(schema)
    #     return schema

    # FIXME: because we are saying that packages of type 'dataset' are handled by ckanext-scheming, this method is not read at all
    # def update_package_schema(self) -> typing.Dict[str, typing.List[typing.Callable]]:
    #     original_schema = super().update_package_schema()
    #     schema = _modify_package_schema(original_schema)
    #     return schema

    # FIXME: because we are saying that packages of type 'dataset' are handled by ckanext-scheming, this method is not read at all
    # def show_package_schema(self) -> typing.Dict[str, typing.List[typing.Callable]]:
    #     schema = super().show_package_schema()
    #
    #     # Don't show vocab tags mixed in with normal 'free' tags
    #     # (e.g. on dataset pages, or on the search page)
    #     schema["tags"]["__extras"].append(toolkit.get_converter("free_tags_only"))
    #
    #     # # Add our custom sasdi_theme metadata field to the schema.
    #     # schema.update(
    #     #     {
    #     #         "sasdi_theme": [
    #     #             toolkit.get_converter("convert_from_tags")(
    #     #                 constants.SASDI_THEMES_VOCABULARY_NAME
    #     #             ),
    #     #             toolkit.get_validator("ignore_missing"),
    #     #         ]
    #     #     }
    #     # )
    #     return schema

    # FIXME: because we are saying that packages of type 'dataset' are handled by ckanext-scheming, this method is not read at all
    # def validate(self, context, data_dict, schema, action):
    #     logger.debug("************************************Inside our validate")
    #     logger.debug(f"{schema=}")
    #     logger.debug("Now calling the sueprclass' validate...")
    #     return super().validate(context, data_dict, schema, action)

    def is_fallback(self) -> bool:
        return True

    def package_types(self) -> typing.List:
        return []

    def get_helpers(self):
        return {
            "dalrrd_emc_dcpr_default_spatial_search_extent": partial(
                helpers.get_default_spatial_search_extent, 0.001
            ),
            "sasdi_themes": helpers.get_sasdi_themes,
            "iso_topic_categories": helpers.get_iso_topic_categories,
        }

    def get_blueprint(self) -> typing.List[Blueprint]:
        return [
            blueprint.dcpr_blueprint,
        ]

    def dataset_facets(
        self, facets_dict: typing.OrderedDict, package_type: str
    ) -> typing.OrderedDict:
        facets_dict.update(
            {
                f"vocab_{constants.SASDI_THEMES_VOCABULARY_NAME}": toolkit._(
                    "SASDI theme"
                ),
                f"vocab_{constants.ISO_TOPIC_CATEGOY_VOCABULARY_NAME}": toolkit._(
                    "ISO Topic Category"
                ),
            }
        )
        return facets_dict

    def group_facets(
        self, facets_dict: typing.OrderedDict, group_type: str, package_type: str
    ) -> typing.OrderedDict:
        """IFacets interface requires reimplementation of all facets-related methods

        In this case we do not really need to override this method, but need to satisfy
        IFacets.

        """

        return facets_dict


def _modify_package_schema(
    schema: typing.Dict[str, typing.List[typing.Callable]]
) -> typing.Dict[str, typing.List[typing.Callable]]:
    schema["sasdi_theme"] = [
        toolkit.get_validator("ignore_missing"),
        toolkit.get_converter("convert_to_tags")(
            constants.SASDI_THEMES_VOCABULARY_NAME
        ),
    ]
    # schema.update(
    #     sasdi_theme=[
    #     toolkit.get_validator("ignore_missing"),
    #     toolkit.get_converter("convert_to_tags")(SASDI_THEMES_VOCABULARY_NAME),
    #     ],

    # these shall be added by the system automatically, but they can be added
    # as hidden fields so that they are not requested from user
    #     metadata_character_set=[],
    #     metadata_standard_name=[],
    #     metadata_standard_version=[],

    # )
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
