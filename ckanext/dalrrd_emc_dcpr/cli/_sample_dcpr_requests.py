import typing
import uuid

from . import (
    _CkanBootstrapDCPRRequest,
)

from ._sample_datasets import SAMPLE_DATASETS


request_dataset = SAMPLE_DATASETS[0]

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
        request_dataset=request_dataset,
        cost="cost",
        spatial_extent="spatial_extent",
        spatial_resolution="EPSG:4326",
        data_capture_urgency="data_capture_urgency",
        additional_information="additional_information",
        request_date="2022-01-01",
        submission_date="2022-01-01",
    )
]
