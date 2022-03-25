import json
import logging
import typing
from pathlib import Path

from ckan.plugins import toolkit

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

    raw_record = json.loads(record_path.read_text())
    main_title = [item for item in raw_record["titles"] if not item.get("titleType")][0]
    notes = [
        i for i in raw_record["descriptions"] if i["descriptionType"] == "Abstract"
    ][0]["description"]
    owner_org = import_mappings.get_owner_org(raw_record["publisher"])
    maintainer_obj = _get_maintainer(raw_record)
    return _CkanEmcDataset(
        name=main_title["title"],
        private=True,
        notes=notes,
        reference_date=[i for i in raw_record["dates"] if i["dateType"] == "Valid"][0][
            "date"
        ],
        iso_topic_category=ISO_TOPIC_CATEGORIES[0][0],
        owner_org=owner_org or "ingestion_org",
        maintainer=maintainer_obj["name"],
        maintainer_email=None,
        resources=_get_resources(raw_record),
        spatial=json.dumps(_get_bbox(raw_record)),
        equivalent_scale="0",
        spatial_representation_type="001",
        spatial_reference_system="EPSG:4326",
        dataset_language=raw_record.get("language", "en-US"),
        metadata_language="en-US",
        dataset_character_set="utf-8",
        type="dataset",
        sasdi_theme=None,
        tags=_get_tags(raw_record),
        source=None,
    )


def _get_maintainer(raw_record: typing.Dict) -> typing.Dict:
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
    maintainer = None
    for contributor in raw_record.get("contributors", []):
        for possible_role in acceptable_maintainer_roles:
            role = contributor.get("contributorType")
            if role == possible_role:
                maintainer = contributor
                break
        if maintainer is not None:
            break
    else:
        maintainer = raw_record.get("contributors", [{"name": "dummy"}])[0]
    return maintainer


def _get_bbox(record: typing.Dict) -> typing.Dict:
    for item in record.get("geoLocations", []):
        reported_box = item.get("geoLocationBox")
        if reported_box:
            min_lon = reported_box["westBoundLongitude"]
            min_lat = reported_box["southBoundLatitude"]
            max_lon = reported_box["eastBoundLongitude"]
            max_lat = reported_box["northBoundLatitude"]
            bbox = {
                "type": "Polygon",
                "coordinates": [
                    [min_lon, min_lat],
                    [max_lon, min_lat],
                    [max_lon, max_lat],
                    [min_lon, max_lat],
                    [min_lon, min_lat],
                ],
            }
            break
    else:  # did not find any geoLocationBox, lets use a default
        bbox = toolkit.h["emc_default_bounding_box"]()
    return bbox


def _get_tags(record: typing.Dict) -> typing.List[typing.Dict]:
    tags = []
    for subject in record["subjects"]:
        tags.append({"name": subject["subject"].strip(), "vocabulary_id": None})
    custom_separator = "**"
    # add the DOI as a tag
    doi = record.get("doi")
    if doi is not None:
        tags.append({"name": f"doi{custom_separator}{doi}", "vocabulary_id": None})
    # add any other related identifiers as tags
    for related_identifier in record.get("relatedIdentifiers", []):
        tags.append(
            {
                "name": custom_separator.join(
                    (
                        related_identifier["relationType"],
                        related_identifier["relatedIdentifierType"],
                        related_identifier["relatedIdentifier"],
                    )
                ),
                "vocabulary_id": None,
            }
        )
    return tags


def _get_resources(record: typing.Dict) -> typing.List[_CkanResource]:
    resources = []
    for linked_resource in record.get("linkedResources", []):
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
