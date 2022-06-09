import typing
import uuid

from . import (
    _CkanBootstrapDcprDataset,
    _CkanBootstrapDCPRRequest,
    _CkanBootstrapDCPRGeospatialRequest,
)


SAMPLE_REQUESTS: typing.Final[typing.List[_CkanBootstrapDCPRRequest]] = [
    _CkanBootstrapDCPRRequest(
        csi_reference_id="sample1",
        proposed_project_name="proposed_project_name",
        additional_project_context="additional_project_context",
        capture_start_date="2022-01-01",
        capture_end_date="2022-01-01",
        cost=200,
        organization_id="sample-org-1",
        spatial_extent="spatial_extent",
        spatial_resolution="EPSG:4326",
        data_capture_urgency="low",
        request_date="2022-01-01",
        submission_date="2022-01-01",
        nsif_review_date="2022-01-01",
        datasets=[
            _CkanBootstrapDcprDataset(
                proposed_dataset_title="some title",
                dataset_purpose="some purpose",
            )
        ],
    )
]


SAMPLE_GEOSPATIAL_REQUESTS: typing.Final[
    typing.List[_CkanBootstrapDCPRGeospatialRequest]
] = [
    _CkanBootstrapDCPRGeospatialRequest(
        csi_reference_id=uuid.UUID("6a68231c-a02c-4c0a-a5e8-7ee325406245"),
        status="status",
        organization_name="organization_name",
        dataset_purpose="dataset_purpose",
        interest_region="interest_region",
        resolution_scale="resolution_scale",
        additional_information="additional_information",
        request_date="2022-01-01",
        submission_date="2022-01-01",
        nsif_review_date="2022-01-01",
        nsif_review_notes="nsif_review_notes",
        nsif_review_additional_documents="nsif_review_additional_documents",
        csi_moderation_notes="csi_moderation_notes",
        csi_review_additional_documents="csi_review_additional_documents",
        csi_moderation_date="2022-01-01",
        dataset_sasdi_category="dataset_sasdi_category",
        custodian_organization="custodian_organization",
        data_type="data_type",
    )
]
