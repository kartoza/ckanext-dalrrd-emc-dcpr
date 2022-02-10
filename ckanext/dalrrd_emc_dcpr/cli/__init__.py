import dataclasses
import datetime as dt
import logging
import typing
from collections.abc import Iterable
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _CkanBootstrapOrganization:
    title: str
    description: str
    image_url: typing.Optional[Path] = None

    @property
    def name(self):
        return self.title.replace(" ", "-").lower()[:100]


@dataclasses.dataclass
class _CkanBootstrapUser:
    name: str
    email: str
    password: str


@dataclasses.dataclass
class _CkanBootstrapHarvester:
    name: str
    url: str
    source_type: str
    update_frequency: str
    configuration: typing.Dict


@dataclasses.dataclass
class _CkanBootstrapResource:
    url: str
    format: str
    format_version: str
    package_id: typing.Optional[str] = None
    description: typing.Optional[str] = None
    resource_type: typing.Optional[str] = None

    def to_data_dict(self):
        logger.debug("Inside to_data_dict of the resource")
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        return result


@dataclasses.dataclass
class _CkanBootstrapEmcDataset:
    name: str
    private: bool
    notes: str
    reference_date: str
    iso_topic_category: str
    owner_org: str
    maintainer: str
    resources: typing.List
    spatial: str
    equivalent_scale: str
    spatial_representation_type: str
    spatial_reference_system: str
    dataset_language: str
    metadata_language: str
    dataset_character_set: str
    maintainer_email: typing.Optional[str] = None
    type: typing.Optional[str] = "dataset"
    sasdi_theme: typing.Optional[str] = None
    tags: typing.Optional[str] = dataclasses.field(default_factory=list)

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        result["title"] = self.name
        result["lineage"] = f"Dummy lineage for {self.name}"
        return result


def _to_data_dict(value: typing.Any):
    if isinstance(value, Iterable):
        try:
            result = [i.to_data_dict() for i in value]
        except AttributeError:
            result = value
    elif getattr(value, "to_data_dict", None) is not None:
        result = value.to_data_dict()
    else:
        result = value
    return result
