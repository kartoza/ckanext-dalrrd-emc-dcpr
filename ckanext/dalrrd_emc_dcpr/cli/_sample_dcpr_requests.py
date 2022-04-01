import typing
import uuid

from . import _CkanBootstrapDCPRRequest, _CkanBootstrapDCPRGeospatialRequest


SAMPLE_REQUESTS: typing.Final[typing.List[_CkanBootstrapDCPRRequest]] = [
    _CkanBootstrapDCPRRequest(
        csi_reference_id=uuid.UUID("9d7f2249-cb25-4ef6-9188-7f8d9efc13d0"),
        status="status",
        organization_name="organization_name",
        organization_level="organization_level",
        organization_address="organization_address",
        proposed_project_name="proposed_project_name",
        additional_project_context="additional_project_context",
        capture_start_date="2022-01-01",
        capture_end_date="2022-01-01",
        cost="cost",
        spatial_extent="spatial_extent",
        spatial_resolution="EPSG:4326",
        data_capture_urgency="data_capture_urgency",
        additional_information="additional_information",
        request_date="2022-01-01",
        submission_date="2022-01-01",
        nsif_review_date="2022-01-01",
        nsif_recommendation="nsif_recommendation",
        nsif_review_notes="nsif_review_notes",
        nsif_review_additional_documents="nsif_review_additional_documents",
        csi_moderation_notes="csi_moderation_notes",
        csi_moderation_additional_documents="csi_moderation_additional_documents",
        csi_moderation_date="2022-01-01",
        dataset_custodian=True,
        data_type="data_type",
        proposed_dataset_title="proposed_dataset_title",
        proposed_abstract="proposed_abstract",
        dataset_purpose="dataset_purpose",
        lineage_statement="lineage_statement",
        associated_attributes="associated_attributes",
        feature_description="feature_description",
        data_usage_restrictions="data_usage_restrictions",
        capture_method="capture_method",
        capture_method_detail="capture_method_detail",
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
