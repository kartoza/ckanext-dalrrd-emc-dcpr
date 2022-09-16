import logging
import typing
from collections import OrderedDict
from functools import partial

import ckan.plugins as plugins
import ckan.lib.helpers as h
import ckan.lib.search as search

import ckan.plugins.toolkit as toolkit
import datetime as dt
import dateutil.parser
from ckan import model
from ckan.common import _, g
from flask import Blueprint
from sqlalchemy import orm

from ckanext.harvest.utils import DATASET_TYPE_NAME as HARVEST_DATASET_TYPE_NAME

from .. import (
    constants,
    helpers,
)
from ..blueprints.dcpr import dcpr_blueprint
from ..blueprints.emc import emc_blueprint
from ..blueprints.xml_parser import xml_parser_blueprint
from ..blueprints.publish import publish_blueprint
from ..cli import commands
from ..cli.legacy_sasdi import commands as legacy_sasdi_commands
from ..logic.action import ckan as ckan_actions
from ..logic.action.dcpr import create as dcpr_create_actions
from ..logic.action.dcpr import delete as dcpr_delete_actions
from ..logic.action.dcpr import get as dcpr_get_actions
from ..logic.action.dcpr import update as dcpr_update_actions
from ..logic.action import emc as emc_actions
from ..logic.action.error_report import create as report_create_actions
from ..logic.action.error_report import update as report_update_actions
from ..logic.action.error_report import get as report_get_actions
from ..logic.action.error_report import delete as report_delete_actions

from ..logic import (
    converters,
    validators,
)
from ..logic.auth import ckan as ckan_auth
from ..logic.auth import pages as ckanext_pages_auth
from ..logic.auth import dcpr as dcpr_auth
from ..logic.auth import emc as emc_auth
from ..logic.auth import error_report as error_report_auth
from ..model.user_extra_fields import UserExtraFields

import ckanext.dalrrd_emc_dcpr.plugins.utils as utils

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
    plugins.implements(plugins.IPluginObserver)

    def before_load(self, plugin_class):
        """IPluginObserver interface requires reimplementation of this method."""
        pass

    def after_load(self, service):
        """Control plugin loading mechanism

        This method is implemented by the DalrrdEmcDcprPlugin because we are adding
        a 1:1 relationship between our `UserExtraFields` model and CKAN's `User` model.

        SQLAlchemy expects relationships to be configured on both sides, which means
        we have to modify CKAN's User model in order to make the relationship work. We
        do that in this function.

        """

        model.User.extra_fields = orm.relationship(
            UserExtraFields, back_populates="user", uselist=False
        )

    def before_unload(self, plugin_class):
        """IPluginObserver interface requires reimplementation of this method."""
        pass

    def after_unload(self, service):
        """IPluginObserver interface requires reimplementation of this method."""
        pass

    def after_create(self, context, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return context, pkg_dict

    def after_delete(self, context, pkg_dict):
        """IPackageController interface requires reimplementation of this method."""
        return context, pkg_dict

    def after_search(self, search_results, search_params):
        """IPackageController interface requires reimplementation of this method."""

        context = {}
        facets = OrderedDict()
        default_facet_titles = {
            "groups": _("Groups"),
            "tags": _("Tags"),
        }

        for facet in h.facets():
            if facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]
            else:
                facets[facet] = facet

        # Facet titles
        for plugin in plugins.PluginImplementations(plugins.IFacets):
            facets = plugin.dataset_facets(facets, "dataset")

        data_dict = {
            "fq": "",
            "facet.field": list(facets.keys()),
        }

        if not getattr(g, "user", None):
            data_dict["fq"] = "+capacity:public " + data_dict["fq"]

        query = search.query_for(model.Package)
        query.run(data_dict, permission_labels=None)

        facets = query.facets

        # organizations in the current search's facets.
        group_names = []
        for field_name in ("groups", "organization"):
            group_names.extend(facets.get(field_name, {}).keys())

        groups = (
            model.Session.query(model.Group.name, model.Group.title)
            .filter(model.Group.name.in_(group_names))
            .all()
            if group_names
            else []
        )
        group_titles_by_name = dict(groups)

        restructured_facets = {}
        for key, value in facets.items():
            restructured_facets[key] = {"title": key, "items": []}
            for key_, value_ in value.items():
                new_facet_dict = {"name": key_}
                if key in ("groups", "organization"):
                    display_name = group_titles_by_name.get(key_, key_)
                    display_name = (
                        display_name if display_name and display_name.strip() else key_
                    )
                    new_facet_dict["display_name"] = display_name
                else:
                    new_facet_dict["display_name"] = key_
                new_facet_dict["count"] = value_
                restructured_facets[key]["items"].append(new_facet_dict)
        search_results["search_facets"] = restructured_facets

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
        search_params["fq"] = utils.handle_search(search_params)
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
        toolkit.add_template_directory(config_, "../templates")
        toolkit.add_public_directory(config_, "../public")
        toolkit.add_resource("../assets", "ckanext-dalrrdemcdcpr")

    def get_commands(self):
        return [
            commands.dalrrd_emc_dcpr,
            legacy_sasdi_commands.legacy_sasdi,
            commands.shell,
        ]

    def get_auth_functions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_publish": ckan_auth.authorize_package_publish,
            "package_update": ckan_auth.package_update,
            "package_patch": ckan_auth.package_patch,
            "dcpr_error_report_create_auth": dcpr_auth.dcpr_report_create_auth,
            "dcpr_request_create_auth": dcpr_auth.dcpr_request_create_auth,
            "my_dcpr_request_list_auth": dcpr_auth.my_dcpr_request_list_auth,
            "dcpr_request_list_public_auth": dcpr_auth.dcpr_request_list_public_auth,
            "dcpr_request_list_private_auth": dcpr_auth.dcpr_request_list_private_auth,
            "dcpr_request_list_under_preparation_auth": dcpr_auth.dcpr_request_list_under_preparation_auth,
            "dcpr_request_list_pending_csi_auth": (
                dcpr_auth.dcpr_request_list_pending_csi_auth
            ),
            "dcpr_request_list_pending_nsif_auth": (
                dcpr_auth.dcpr_request_list_pending_nsif_auth
            ),
            "dcpr_request_show_auth": dcpr_auth.dcpr_request_show_auth,
            "dcpr_request_update_by_owner_auth": dcpr_auth.dcpr_request_update_by_owner_auth,
            "dcpr_request_update_by_nsif_auth": dcpr_auth.dcpr_request_update_by_nsif_auth,
            "dcpr_request_update_by_csi_auth": dcpr_auth.dcpr_request_update_by_csi_auth,
            "dcpr_request_submit_auth": dcpr_auth.dcpr_request_submit_auth,
            "dcpr_request_claim_nsif_reviewer_auth": dcpr_auth.dcpr_request_claim_nsif_reviewer_auth,
            "dcpr_request_claim_csi_moderator_auth": dcpr_auth.dcpr_request_claim_csi_moderator_auth,
            "dcpr_request_resign_nsif_reviewer_auth": dcpr_auth.dcpr_request_resign_nsif_reviewer_auth,
            "dcpr_request_resign_csi_reviewer_auth": dcpr_auth.dcpr_request_resign_csi_reviewer_auth,
            "dcpr_request_nsif_moderate_auth": dcpr_auth.dcpr_request_nsif_moderate_auth,
            "dcpr_request_csi_moderate_auth": dcpr_auth.dcpr_request_csi_moderate_auth,
            "dcpr_request_delete_auth": dcpr_auth.dcpr_request_delete_auth,
            "ckanext_pages_update": ckanext_pages_auth.authorize_edit_page,
            "ckanext_pages_delete": ckanext_pages_auth.authorize_delete_page,
            "ckanext_pages_show": ckanext_pages_auth.authorize_show_page,
            "emc_request_dataset_maintenance": (
                emc_auth.authorize_request_dataset_maintenance
            ),
            "emc_request_dataset_publication": (
                emc_auth.authorize_request_dataset_publication
            ),
            "error_report_create_auth": error_report_auth.error_report_create_auth,
            "error_report_update_by_owner_auth": error_report_auth.error_report_update_by_owner_auth,
            "error_report_update_by_nsif_auth": error_report_auth.error_report_update_by_nsif_auth,
            "error_report_nsif_moderate_auth": error_report_auth.error_report_nsif_moderate_auth,
            "my_error_reports_auth": error_report_auth.my_error_reports_auth,
            "error_report_submitted_auth": error_report_auth.error_report_submitted_auth,
            "error_report_list_public_auth": error_report_auth.error_report_list_public_auth,
            "my_error_report_list_auth": error_report_auth.my_error_report_list_auth,
            "error_report_delete_auth": error_report_auth.error_report_delete_auth,
        }

    def get_actions(self) -> typing.Dict[str, typing.Callable]:
        return {
            "package_create": ckan_actions.package_create,
            "package_update": ckan_actions.package_update,
            "package_patch": ckan_actions.package_patch,
            "dcpr_error_report_create": dcpr_create_actions.dcpr_error_report_create,
            "dcpr_request_create": dcpr_create_actions.dcpr_request_create,
            "dcpr_geospatial_request_create": (
                dcpr_create_actions.dcpr_geospatial_request_create
            ),
            "dcpr_request_list_public": dcpr_get_actions.dcpr_request_list_public,
            "dcpr_request_list_under_preparation": dcpr_get_actions.dcpr_request_list_under_preparation,
            "my_dcpr_request_list": dcpr_get_actions.my_dcpr_request_list,
            "dcpr_request_list_awaiting_csi_moderation": (
                dcpr_get_actions.dcpr_request_list_awaiting_csi_moderation
            ),
            "dcpr_request_list_awaiting_nsif_moderation": (
                dcpr_get_actions.dcpr_request_list_awaiting_nsif_moderation
            ),
            "dcpr_request_show": dcpr_get_actions.dcpr_request_show,
            "dcpr_request_update_by_owner": dcpr_update_actions.dcpr_request_update_by_owner,
            "dcpr_request_submit": dcpr_update_actions.dcpr_request_submit,
            "dcpr_request_update_by_nsif": dcpr_update_actions.dcpr_request_update_by_nsif,
            "dcpr_request_update_by_csi": dcpr_update_actions.dcpr_request_update_by_csi,
            "claim_dcpr_request_nsif_reviewer": dcpr_update_actions.claim_dcpr_request_nsif_reviewer,
            "claim_dcpr_request_csi_reviewer": dcpr_update_actions.claim_dcpr_request_csi_reviewer,
            "resign_dcpr_request_nsif_reviewer": dcpr_update_actions.resign_dcpr_request_nsif_reviewer,
            "resign_dcpr_request_csi_reviewer": dcpr_update_actions.resign_dcpr_request_csi_reviewer,
            "dcpr_request_nsif_moderate": dcpr_update_actions.dcpr_request_nsif_moderate,
            "dcpr_request_csi_moderate": dcpr_update_actions.dcpr_request_csi_moderate,
            "dcpr_request_delete": dcpr_delete_actions.dcpr_request_delete,
            "emc_version": emc_actions.show_version,
            "emc_request_dataset_maintenance": emc_actions.request_dataset_maintenance,
            "emc_request_dataset_publication": emc_actions.request_dataset_publication,
            "emc_user_patch": ckan_actions.user_patch,
            "user_update": ckan_actions.user_update,
            "user_create": ckan_actions.user_create,
            "user_show": ckan_actions.user_show,
            "error_report_create": report_create_actions.error_report_create,
            "error_report_update_by_owner": report_update_actions.error_report_update_by_owner,
            "error_report_update_by_nsif": report_update_actions.error_report_update_by_nsif,
            "error_report_show": report_get_actions.error_report_show,
            "error_report_list_public": report_get_actions.error_report_list_public,
            "my_error_report_list": report_get_actions.my_error_report_list,
            "submitted_error_report_list_": report_get_actions.submitted_error_report_list,
            "error_report_delete": report_delete_actions.error_report_delete,
        }

    def get_validators(self) -> typing.Dict[str, typing.Callable]:
        return {
            "value_or_true": validators.emc_value_or_true_validator,
            "emc_srs_validator": validators.emc_srs_validator,
            "emc_bbox_converter": converters.emc_bbox_converter,
            "dcpr_end_date_after_start_date_validator": validators.dcpr_end_date_after_start_date_validator,
            "dcpr_moderation_choices_validator": validators.dcpr_moderation_choices_validator,
            "spatial_resolution_converter": converters.spatial_resolution_converter,
            "convert_choices_select_to_int": converters.convert_choices_select_to_int,
            "convert_select_custom_choice_to_extra": converters.convert_select_custom_choice_to_extra,
            # "expand_tags_composite": converters.expand_tags_composite,
        }

    def is_fallback(self) -> bool:
        return False

    def package_types(self) -> typing.List:
        return []

    def get_helpers(self):
        return {
            "dalrrd_emc_dcpr_default_spatial_search_extent": partial(
                helpers.get_default_spatial_search_extent, 0.001
            ),
            "emc_build_nav_main": helpers.build_pages_nav_main,
            "emc_default_bounding_box": helpers.get_default_bounding_box,
            "emc_convert_geojson_to_bounding_box": helpers.convert_geojson_to_bbox,
            "emc_extent_to_bbox": helpers.convert_string_extent_to_bbox,
            "emc_sasdi_themes": helpers.get_sasdi_themes,
            "emc_iso_topic_categories": helpers.get_iso_topic_categories,
            "emc_show_version": helpers.helper_show_version,
            "emc_user_is_org_member": helpers.user_is_org_member,
            "emc_org_member_list": helpers.org_member_list,
            "emc_user_is_staff_member": helpers.user_is_staff_member,
            "emc_get_featured_datasets": helpers.get_featured_datasets,
            "emc_get_recently_modified_datasets": helpers.get_recently_modified_datasets,
            "emc_get_all_datasets_count": helpers.get_all_datasets_count,
            "dcpr_get_next_intermediate_dcpr_request_status": helpers.get_next_intermediate_dcpr_status,
            "dcpr_user_is_dcpr_request_owner": helpers.user_is_dcpr_request_owner,
            "emc_org_memberships": helpers.get_org_memberships,
            # added by mohab
            "dcpr_requests_approved_by_nsif": helpers.get_dcpr_requests_approved_by_nsif,
            "is_dcpr_request": helpers.is_dcpr_request,
            "get_dcpr_request_action": helpers.get_dcpr_request_action,
            "mod_scheming_flatten_subfield": helpers.mod_scheming_flatten_subfield,
            "get_today_date": helpers.get_today_date,
            "get_maintenance_custom_other_field_data": helpers.get_maintenance_custom_other_field_data,
        }

    def get_blueprint(self) -> typing.List[Blueprint]:
        return [
            dcpr_blueprint,
            emc_blueprint,
            xml_parser_blueprint,
            publish_blueprint,
        ]

    def dataset_facets(
        self, facets_dict: typing.OrderedDict, package_type: str
    ) -> typing.OrderedDict:
        if package_type != HARVEST_DATASET_TYPE_NAME:
            facets_dict[f"vocab_{constants.SASDI_THEMES_VOCABULARY_NAME}"] = toolkit._(
                "SASDI Themes"
            )
            facets_dict[
                f"vocab_{constants.ISO_TOPIC_CATEGOY_VOCABULARY_NAME}"
            ] = toolkit._("ISO Topic Categories")
            facets_dict["reference_date"] = toolkit._("Reference Date")
            facets_dict["harvest_source_title"] = toolkit._("Harvest source")
            facets_dict["dcpr_request"] = toolkit._("DCPR Request")
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
