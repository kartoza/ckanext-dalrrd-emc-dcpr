import datetime as dt
import logging
import pathlib
import typing

import dateutil.parser
import langcodes
import yaml
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model.license import LicenseNotSpecified

from ckanext.spatial.interfaces import ISpatialHarvester

from ..cli import _CkanEmcDataset, _CkanResource

logger = logging.getLogger(__name__)


class HarvestingPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    """Custom plugin to deal with harvesting-related customizations.

    This class exists in order to work around a bug in ckanext-spatial:

        https://github.com/ckan/ckanext-spatial/issues/277

    The mentioned bug prevents being able to have a CKAN extension plugin using both
    the `IValidators` and the `ISpatialHarvester` interfaces at the same time.

    As an alternative, we have implemented the current plugin class with the aim
    to use it strictly for customization of the harvesters (_i.e._ implement the
    ISpatialHarvester interface) while the main plugin class
    (emc_dcpr_plugin.DalrrdEmcDcprPlugin) is still handling all of the other EMC-DCPR
    customizations.

    """

    plugins.implements(ISpatialHarvester, inherit=True)

    def get_package_dict(
        self, context: typing.Dict, data_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """Extension point required by ISpatialHarvester"""
        package_dict = data_dict.get("package_dict", {})
        iso_values = data_dict.get("iso_values", {})
        parsed_resources = []
        for resource_dict in package_dict.get("resources", []):
            parsed_resources.append(
                _CkanResource(
                    url=resource_dict.get("url"),
                    format=resource_dict.get("format"),
                    format_version="change me",
                    name=resource_dict.get("name"),
                    description=resource_dict.get("description") or None,
                )
            )
        parsed_tags = []
        for parsed_tag in package_dict.get("tags", []):
            parsed_tags.append(
                {"name": parsed_tag.get("name", ""), "vocabulary_id": None}
            )
        declared_dataset_language = _get_possibly_list_item(
            iso_values, "dataset-language"
        )
        dataset_language = _get_language_code(declared_dataset_language or "en")
        iso_topic_category = _get_possibly_list_item(iso_values, "topic-category")
        equivalent_scale = _get_possibly_list_item(iso_values, "equivalent-scale")
        dataset = _CkanEmcDataset(
            type="dataset",
            private=True,
            featured=False,
            name=package_dict.get("name"),
            title=package_dict.get("title"),
            notes=package_dict.get("notes"),
            iso_topic_category=iso_topic_category or "",
            owner_org=package_dict.get("owner_org"),
            lineage=iso_values.get("lineage"),
            metadata_language=_get_language_code(iso_values.get("metadata-language")),
            equivalent_scale=equivalent_scale or "1",
            dataset_language=dataset_language,
            dataset_character_set="utf-8",  # this may not be correct, but publisher is able to correct before publishing
            maintainer=iso_values.get("contact"),
            maintainer_email=iso_values.get("contact-email"),
            license_id=LicenseNotSpecified.id,  # set this default and let publisher adjust
            spatial=_get_spatial_field(package_dict),
            spatial_reference_system="EPSG:4326",
            resources=parsed_resources,
            tags=parsed_tags,
            reference_date=_get_reference_date(iso_values),
            sasdi_theme=None,  # seems like we can't know the SASDI theme in advance
            spatial_representation_type="001",
            source=None,
            version=None,
        )
        # add these to the data_dict:
        # - id: this lets ckanext.harvest know whether to create or update a dataset
        # - metadata_modified
        new_data_dict = dataset.to_data_dict()
        new_data_dict["id"] = iso_values.get("guid")
        new_data_dict["metadata_modified"] = iso_values.get("date_updated")
        return new_data_dict


def _get_reference_date(iso_values: typing.Dict) -> str:
    fallback_reference_date = dt.datetime.now(dt.timezone.utc).isoformat()
    if (raw_temp_extent_begin := iso_values.get("temporal-extent-begin")) is not None:
        if isinstance(raw_temp_extent_begin, list):
            try:
                temp_extent_begin = raw_temp_extent_begin[0]
            except IndexError:
                temp_extent_begin = None
        else:
            temp_extent_begin = raw_temp_extent_begin
        try:
            reference_date = dateutil.parser.parse(temp_extent_begin)
        except (TypeError, dateutil.parser.ParserError):
            logger.exception(msg=f"Could not parse {temp_extent_begin!r} as a datetime")
            result = fallback_reference_date
        else:
            result = reference_date.isoformat()
    else:
        for related_date in iso_values.get("dataset-reference-date", []):
            if related_date.get("type", "publication") == "creation":
                if (raw_date := related_date.get("value")) is not None:
                    try:
                        reference_date = dateutil.parser.parse(raw_date)
                    except dateutil.parser.ParserError:
                        logger.exception(
                            msg=f"Could not parse {raw_date!r} as a datetime"
                        )
                        result = fallback_reference_date
                    else:
                        result = reference_date.isoformat()
                break
        else:
            try:
                raw_date = iso_values["dataset-reference-date"][0]["value"]
                if raw_date is not None:
                    try:
                        reference_date = dateutil.parser.parse(raw_date)
                    except dateutil.parser.ParserError:
                        logger.exception(
                            msg=f"Could not parse {raw_date!r} as a datetime"
                        )
                        result = fallback_reference_date
                    else:
                        result = reference_date.isoformat()
            except (KeyError, IndexError):
                result = fallback_reference_date
    return result


def _get_possibly_list_item(mapping: typing.Mapping, key: str) -> typing.Optional[str]:
    value = mapping.get(key)
    if isinstance(value, list):
        try:
            value = value[0]
        except IndexError:
            value = None
    return value


def _get_spatial_field(package: typing.Dict):
    for extra_field in package.get("extras", []):
        if extra_field["key"] == "spatial":
            spatial = extra_field["value"]
    else:
        spatial = toolkit.config.get(
            "ckan.dalrrd_emc_dcpr.default_spatial_search_extent"
        )
    return spatial


def _get_allowed_dataset_languages() -> typing.List[str]:
    dataset_schema_path = (
        pathlib.Path(__file__).parents[1] / "scheming/dataset_schema.yaml"
    )
    result = []
    if dataset_schema_path.exists():
        dataset_schema = yaml.safe_load(dataset_schema_path.read_text())
        for field_params in dataset_schema.get("dataset_fields"):
            if field_params["field_name"] == "dataset_language":
                for choice in field_params.get("choices", []):
                    result.append(choice["value"])
    return result


def _get_language_code(source_code: str) -> str:
    allowed_choices = _get_allowed_dataset_languages()
    default_language_code = "en"
    result = default_language_code
    try:
        target_code = langcodes.standardize_tag(langcodes.Language(source_code))
    except ValueError:
        logger.exception(
            msg=(
                f"Could not recognize language code {source_code}, applying default "
                f"language code of {default_language_code}"
            )
        )
    else:
        result = default_language_code
        if target_code in allowed_choices:
            result = target_code
        else:
            logger.debug(
                f"language code {result} is not allowed, applying default language code "
                f"of {default_language_code}"
            )
    return result
