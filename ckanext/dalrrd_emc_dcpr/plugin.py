import logging
import typing
from functools import partial

from flask import Blueprint

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from . import (
    constants,
    helpers,
)
from .blueprints.dcpr import dcpr_blueprint
from .blueprints.emc import emc_blueprint
from .cli import commands
from .logic.action import ckan as ckan_actions
from .logic.action import dcpr as dcpr_actions
from .logic.action import emc as emc_actions
from .logic import (
    converters,
    validators,
)
from .logic.auth import dcpr as dcpr_auth
from .logic.auth import ckan as ckan_auth

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
        toolkit.add_resource("assets", "ckanext-dalrrdemcdcpr")

    def get_commands(self):
        return [
            commands.dalrrd_emc_dcpr,
        ]

    def get_auth_functions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_publish": ckan_auth.authorize_package_publish,
            "package_update": ckan_auth.package_update,
            "package_patch": ckan_auth.package_patch,
            "dcpr_request_list_auth": dcpr_auth.dcpr_request_list_auth,
        }

    def get_actions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_create": ckan_actions.package_create,
            "package_update": ckan_actions.package_update,
            "package_patch": ckan_actions.package_patch,
            "dcpr_request_list": dcpr_actions.dcpr_request_list,
            "emc_version": emc_actions.show_version,
        }

    def get_validators(self) -> typing.Dict[str, typing.Callable]:
        return {
            "value_or_true": validators.emc_value_or_true_validator,
            "emc_srs_validator": validators.emc_srs_validator,
            "emc_bbox_converter": converters.emc_bbox_converter,
        }

    def is_fallback(self) -> bool:
        return True

    def package_types(self) -> typing.List:
        return []

    def get_helpers(self):
        return {
            "dalrrd_emc_dcpr_default_spatial_search_extent": partial(
                helpers.get_default_spatial_search_extent, 0.001
            ),
            "emc_default_bounding_box": helpers.get_default_bounding_box,
            "emc_convert_geojson_to_bounding_box": helpers.convert_geojson_to_bbox,
            "emc_sasdi_themes": helpers.get_sasdi_themes,
            "emc_iso_topic_categories": helpers.get_iso_topic_categories,
            "emc_show_version": helpers.helper_show_version,
            "emc_user_is_org_member": helpers.user_is_org_member,
        }

    def get_blueprint(self) -> typing.List[Blueprint]:
        return [
            dcpr_blueprint,
            emc_blueprint,
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
