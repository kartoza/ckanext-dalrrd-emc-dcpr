import logging
import typing
from functools import partial

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import datetime as dt
import dateutil.parser
from flask import Blueprint

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
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IFacets)

    def after_create(self, context, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return context, pkg_dict

    def after_delete(self, context, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return context, pkg_dict

    def after_search(self, search_results, search_params):
        """IPackageController interface requires reimplementation of this method."""
        return search_results

    def after_show(self, context, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return context, pkg_dict

    def after_update(self, context, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return context, pkg_dict

    def before_index(self, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return pkg_dict

    def before_search(self, search_params: typing.Dict):
        start_date = search_params.get("extras", {}).get("ext_start_reference_date")
        end_date = search_params.get("extras", {}).get("ext_end_reference_date")
        if start_date is not None or end_date is not None:
            parsed_start = _parse_date(start_date) if start_date else start_date
            parsed_end = _parse_date(end_date) if end_date else end_date
            temporal_query = (
                f"reference_date:[{parsed_start or '*'} TO {parsed_end or '*'}]"
            )
            filter_query = " ".join((search_params["fq"], temporal_query))
            search_params["fq"] = filter_query
        return search_params

    def before_view(self, pkg_dict: typing.Dict):
        return pkg_dict

    def create(self, entity):
        """IPackageController interface requires reimplementation of this method."""
        return entity

    def edit(self, entity):
        """IPackageController interface requires reimplementation of this method."""
        return entity

    def delete(self, entity):
        """IPackageController interface requires reimplementation of this method."""
        return entity

    def read(self, entity):
        """IPackageController interface requires reimplementation of this method."""
        return entity

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
            "dcpr_request_create_auth": dcpr_auth.dcpr_request_create_auth,
            "dcpr_request_list_auth": dcpr_auth.dcpr_request_list_auth,
        }

    def get_actions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_create": ckan_actions.package_create,
            "package_update": ckan_actions.package_update,
            "package_patch": ckan_actions.package_patch,
            "dcpr_request_create": dcpr_actions.dcpr_request_create,
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
        facets_dict[f"vocab_{constants.SASDI_THEMES_VOCABULARY_NAME}"] = toolkit._(
            "SASDI Theme"
        )
        facets_dict[f"vocab_{constants.ISO_TOPIC_CATEGOY_VOCABULARY_NAME}"] = toolkit._(
            "ISO Topic Category"
        )
        facets_dict["reference_date"] = toolkit._("Reference Date")
        return facets_dict

    def group_facets(
        self, facets_dict: typing.OrderedDict, group_type: str, package_type: str
    ) -> typing.OrderedDict:
        """IFacets interface requires reimplementation of all facets-related methods

        In this case we do not really need to override this method, but need to satisfy
        IFacets.

        """

        return facets_dict


def _parse_date(raw_date: str) -> typing.Optional[str]:
    """Parse user-submitted date into a string usable in Solr searches."""
    try:
        parsed_date = dateutil.parser.parse(raw_date, ignoretz=True).replace(
            tzinfo=dt.timezone.utc
        )
        result = parsed_date.isoformat().replace("+00:00", "Z")
    except dateutil.parser.ParserError:
        logger.exception("Could not parse date from input string")
        result = None
    return result
