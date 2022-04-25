import datetime as dt
import json
import logging
import typing
from pathlib import Path

import dateutil.parser
from ckan.plugins import toolkit
from slugify import slugify

from ....constants import ISO_TOPIC_CATEGORIES
from ... import _CkanEmcDataset, _CkanResource
from .. import import_mappings

logger = logging.getLogger(__name__)


def parse_record(record_path: Path):
    """Parse the raw JSON record into a Dataset object

    Parsing is done based on the jsonschema saeon_datacite_4.3_schema.json jsonschema

    NOTES:

        - There seems to be no structured way to provide an email for a `creator` or
          `contributor` in the datacite scheme used by SAEON's ODP
        - The `geolocations` property is not mandatory in the datacite schema, so it is
          possible that some records do not have information about their own geospatial
          extent. In that case we provide a default extent
        - It may be possible able to extract additional info, such as the iso topic
          category from the record's `originalMetadata` property, if it exists

    """

    # logger.debug(f"parsing {str(record_path)!r}...")
    raw_record = json.loads(record_path.read_text())
    main_title = [item for item in raw_record["titles"] if not item.get("titleType")][0]
    name = slugify(main_title["title"])[:100]
    notes = [
        i for i in raw_record["descriptions"] if i["descriptionType"] == "Abstract"
    ][0].get("description", "There is no additional information about the dataset")
    owner_org = import_mappings.get_owner_org(raw_record["publisher"])
    maintainer = _get_maintainer(raw_record, record_path)
    return _CkanEmcDataset(
        name=name,
        title=main_title["title"],
        private=True,
        notes=notes,
        reference_date=_get_reference_date(raw_record),
        iso_topic_category=ISO_TOPIC_CATEGORIES[0][0],
        owner_org=owner_org,
        maintainer=maintainer,
        maintainer_email=None,
        resources=_get_resources(raw_record),
        spatial=",".join(str(i) for i in _get_bbox(raw_record)),
        equivalent_scale="0",
        spatial_representation_type="001",
        spatial_reference_system="EPSG:4326",
        dataset_language=raw_record.get("language", "en").partition("-")[0],
        metadata_language="en",
        dataset_character_set="utf-8",
        type="dataset",
        sasdi_theme=None,
        tags=_get_tags(raw_record, record_path),
        source=None,
    )


def _get_reference_date(record: typing.Dict) -> str:
    # the jsonschema file has `dates` as mandatory, but some of the legacy data data does not have this element
    for date_ in record.get("dates", []):
        if date_["dateType"] == "Valid":
            # the provided date may be a range, in which case it is separated by a slash
            # the format is described here:
            #
            # http://www.ukoln.ac.uk/metadata/dcmi/collection-RKMS-ISO8601/
            #
            start, end = date_["date"].partition("/")[::2]
            if start and end:
                # since our schema expects the reference date to be a single temporal
                # value, we arbitrarily choose the start of the period as the
                # reference date
                raw_referece_date = start
            elif start:
                raw_referece_date = start
            else:
                raw_referece_date = end
            break
    else:
        raw_referece_date = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%d")
    parsed = dateutil.parser.parse(raw_referece_date)
    return parsed.strftime("%Y-%m-%d")


def _get_maintainer(record: typing.Dict, record_path: Path) -> str:
    acceptable_maintainer_roles = [
        "ContactPerson",
        "DataCollector",
        "DataCurator",
        "DataManager",
        "Distributor",
        "Editor",
        "Producer",
        "ProjectLeader",
        "ProjectManager",
        "ProjectMember",
        "Supervisor",
        "WorkPackageLeader",
    ]
    placeholder = "placeholder, please change"
    for contributor in record.get("contributors", []):
        role = contributor.get("contributorType")
        if role in acceptable_maintainer_roles:
            try:
                maintainer = contributor["name"]
            except KeyError:
                try:
                    maintainer = contributor.get("affiliation", [])[0].get(
                        "afilliation", placeholder
                    )
                except IndexError:
                    maintainer = placeholder
            break
    else:
        maintainer = placeholder
    return maintainer


def _get_bbox(record: typing.Dict) -> typing.Dict:
    for item in record.get("geoLocations", []):
        reported_box = item.get("geoLocationBox")
        reported_point = item.get("geoLocationPoint")
        if reported_box:
            min_lon = reported_box["westBoundLongitude"]
            min_lat = reported_box["southBoundLatitude"]
            max_lon = reported_box["eastBoundLongitude"]
            max_lat = reported_box["northBoundLatitude"]
        elif reported_point:
            mid_lon = reported_point["pointLongitude"]
            mid_lat = reported_point["pointLatitude"]
            box_width_degrees = 0.001
            min_lon = mid_lon - box_width_degrees
            max_lon = mid_lon + box_width_degrees
            min_lat = mid_lat - box_width_degrees
            max_lat = mid_lat + box_width_degrees
        if reported_box or reported_point:
            geojson_bbox = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ],
                ],
            }
            break
    else:  # did not find any geoLocationBox, lets use a default
        geojson_bbox = toolkit.h["dalrrd_emc_dcpr_default_spatial_search_extent"]()
    return toolkit.h["emc_convert_geojson_to_bounding_box"](geojson_bbox)


def _build_tag_name(raw_name: str) -> typing.Optional[str]:
    name = slugify(raw_name.strip())
    return name if 2 <= len(name) < 100 else None


def _get_tags(record: typing.Dict, record_path: Path) -> typing.List[typing.Dict]:
    tags = [
        {
            "name": import_mappings.IMPORT_TAG_NAME,
            "vocabulary_id": None,
        },
        {
            "name": f"import-filename-{record_path.name}",
            "vocabulary_id": None,
        },
    ]
    custom_separator = "__"
    for subject in record["subjects"]:
        name = _build_tag_name(subject["subject"])
        if name:
            tags.append({"name": name, "vocabulary_id": None})
    # add any additional file identifiers as extra tags
    file_identifier = record.get("fileIdentifier")
    if file_identifier is not None:
        name = _build_tag_name(
            f"fileIdentifier{custom_separator}{slugify(file_identifier)}"
        )
        if name:
            tags.append({"name": name, "vocabulary_id": None})
    # add any other identifiers
    for identifier in record.get("identifiers", []):
        name = _build_tag_name(
            custom_separator.join(
                (identifier["identifierType"], identifier["identifier"])
            )
        )
        if name:
            tags.append({"name": name, "vocabulary_id": None})
    # add any other related identifiers
    for related_identifier in record.get("relatedIdentifiers", []):
        name = _build_tag_name(
            custom_separator.join(
                (
                    related_identifier["relationType"],
                    related_identifier["relatedIdentifierType"],
                    related_identifier["relatedIdentifier"],
                )
            )
        )
        if name:
            tags.append({"name": name, "vocabulary_id": None})
    return tags


def _get_resources(record: typing.Dict) -> typing.List[_CkanResource]:
    resources = []
    for linked_resource in record.get("linkedResources", []):
        url = linked_resource.get("resourceURL")
        if url is not None:
            resources.append(
                _CkanResource(
                    url=linked_resource["resourceURL"],
                    format=linked_resource.get("resourceFormat"),
                    format_version="1",
                    resource_type=linked_resource["linkedResourceType"],
                    name=linked_resource.get("resourceName"),
                    description=linked_resource.get("resourceDescription"),
                )
            )
    return resources
