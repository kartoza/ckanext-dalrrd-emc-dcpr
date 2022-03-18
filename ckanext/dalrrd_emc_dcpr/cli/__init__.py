import dataclasses
import logging
import typing
import uuid
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

    def to_data_dict(self) -> typing.Dict:
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
    tags: typing.List[typing.Dict] = dataclasses.field(default_factory=list)

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        result["title"] = self.name
        result["lineage"] = f"Dummy lineage for {self.name}"
        return result


@dataclasses.dataclass
class _CkanBootstrapDCPRRequest:
    csi_reference_id: uuid.UUID
    status: str
    organization_name: str
    organization_level: str
    organization_address: str
    proposed_project_name: str
    additional_project_context: str
    capture_start_date: str
    capture_end_date: str
    cost: str
    spatial_extent: str
    spatial_resolution: str
    data_capture_urgency: str
    additional_information: str
    request_date: str
    submission_date: str
    nsif_review_date: str
    nsif_recommendation: str
    nsif_review_notes: str
    nsif_review_additional_documents: str
    csi_moderation_notes: str
    csi_moderation_additional_documents: str
    csi_moderation_date: str
    dataset_custodian: bool
    data_type: str
    purposed_dataset_title: str
    purposed_abstract: str
    dataset_purpose: str
    lineage_statement: str
    associated_attributes: str
    feature_description: str
    data_usage_restrictions: str
    capture_method: str
    capture_method_detail: str

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        return result


@dataclasses.dataclass
class _CkanBootstrapDCPRGeospatialRequest:
    csi_reference_id: uuid.UUID
    status: str
    organization_name: str
    dataset_purpose: str
    interest_region: str
    resolution_scale: str
    additional_information: str
    request_date: str
    submission_date: str
    nsif_review_date: str
    nsif_review_notes: str
    nsif_review_additional_documents: str
    csi_moderation_notes: str
    csi_review_additional_documents: str
    csi_moderation_date: str
    dataset_sasdi_category: str
    custodian_organization: str
    data_type: str

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        return result


@dataclasses.dataclass
class _CkanExtBootstrapPage:
    name: str
    content: str
    private: bool
    org_id: typing.Optional[str] = None
    order: typing.Optional[str] = ""
    page_type: typing.Optional[str] = "page"
    user_id: typing.Optional[str] = None

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        result["title"] = self.name.capitalize()
        return result


def _to_data_dict(value):
    if isinstance(value, str):
        result = value
    elif isinstance(value, Iterable):
        try:
            result = [i.to_data_dict() for i in value]
        except AttributeError:
            result = list(value)
    elif getattr(value, "to_data_dict", None) is not None:
        result = value.to_data_dict()
    else:
        result = value
    return result
