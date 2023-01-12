import dataclasses
import logging
import typing
import uuid
import collections.abc
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _CkanBootstrapOrganization:
    name: str
    title: str
    description: str
    image_url: typing.Optional[Path] = None


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
class _CkanResource:
    url: str
    format: str
    format_version: str
    package_id: typing.Optional[str] = None
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    resource_type: typing.Optional[str] = None

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        return result


@dataclasses.dataclass
class _CkanEmcDataset:
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
    title: typing.Optional[str] = None
    maintainer_email: typing.Optional[str] = None
    type: typing.Optional[str] = "dataset"
    sasdi_theme: typing.Optional[str] = None
    tags: typing.List[typing.Dict] = dataclasses.field(default_factory=list)
    source: typing.Optional[str] = None
    license_id: typing.Optional[str] = None
    version: typing.Optional[str] = None
    lineage: typing.Optional[str] = None
    featured: typing.Optional[bool] = False

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        if result.get("title") is None:
            result["title"] = self.name
        result["lineage"] = f"Dummy lineage for {self.name}"
        return result


@dataclasses.dataclass
class _CkanBootstrapErrorReport:
    csi_reference_id: uuid.UUID
    status: str
    error_application: str
    error_description: str
    solution_description: str
    request_date: str
    nsif_review_additional_documents: str
    nsif_moderation_notes: str
    nsif_moderation_date: str

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        return result


@dataclasses.dataclass
class _CkanBootstrapDcprDataset:
    proposed_dataset_title: str
    dataset_purpose: str
    dataset_custodian: typing.Optional[bool] = False
    data_type: typing.Optional[str] = None
    proposed_abstract: typing.Optional[str] = None
    lineage_statement: typing.Optional[str] = None
    associated_attributes: typing.Optional[str] = None
    data_usage_restrictions: typing.Optional[str] = None
    capture_method: typing.Optional[str] = None

    def to_data_dict(self) -> typing.Dict:
        result = {}
        for name, value in vars(self).items():
            if value is not None:
                result[name] = _to_data_dict(value)
        return result


@dataclasses.dataclass
class _CkanBootstrapDCPRRequest:
    proposed_project_name: str
    capture_start_date: str
    capture_end_date: str
    cost: int
    organization_id: str
    request_date: str
    csi_reference_id: typing.Optional[str] = None
    csi_moderator: typing.Optional[str] = None
    nsif_reviewer: typing.Optional[str] = None
    additional_project_context: typing.Optional[str] = ""
    spatial_extent: typing.Optional[str] = None
    spatial_resolution: typing.Optional[str] = None
    data_capture_urgency: typing.Optional[str] = "low"
    submission_date: typing.Optional[str] = None
    nsif_review_date: typing.Optional[str] = None
    nsif_review_notes: typing.Optional[str] = None
    csi_moderation_date: typing.Optional[str] = None
    datasets: typing.List[_CkanBootstrapDcprDataset] = dataclasses.field(
        default_factory=list
    )
    # organization_name: str
    # organization_level: str
    # organization_address: str
    # additional_information: str
    # nsif_recommendation: str
    # nsif_review_additional_documents: str
    # csi_moderation_notes: str
    # csi_moderation_additional_documents: str

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
    if isinstance(value, (str, int, float)):
        result = value
    elif isinstance(value, collections.abc.Mapping):
        result = value
    elif isinstance(value, collections.abc.Iterable):
        result = [_to_data_dict(i) for i in value]
    elif getattr(value, "to_data_dict", None) is not None:
        result = value.to_data_dict()
    else:
        result = _to_data_dict(value)
    return result
