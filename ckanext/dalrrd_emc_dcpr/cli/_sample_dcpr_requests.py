import json
import typing
import uuid
from datetime import datetime

from . import (
    _CkanBootstrapDCPRRequest,
    _CkanBootstrapEmcDataset,
    _CkanBootstrapResource,
)


request_dataset = _CkanBootstrapEmcDataset(
    name="sample-ds-1",
    private=False,
    notes="Abstract for sample-ds-1",
    reference_date="2022-01-01",
    iso_topic_category="biota",
    owner_org="sample-org-1",
    maintainer="Nobody, No One, Ms.",
    resources=[
        _CkanBootstrapResource("http://fake.com", format="shp", format_version="1")
    ],
    spatial=json.dumps(
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [10.0, 10.0],
                    [10.31, 10.0],
                    [10.31, 10.44],
                    [10.0, 10.44],
                    [10.0, 10.0],
                ]
            ],
        }
    ),
    equivalent_scale="500",
    spatial_representation_type="001",
    spatial_reference_system="EPSG:4326",
    dataset_language="en",
    metadata_language="en",
    dataset_character_set="utf-8",
)

SAMPLE_REQUESTS: typing.Final[typing.List[_CkanBootstrapDCPRRequest]] = [
    _CkanBootstrapDCPRRequest(
        csi_reference_id=uuid.uuid4(),
        status="status",
        organization_name="organization_name",
        organization_level="organization_level",
        organization_address="organization_address",
        proposed_project_name="proposed_project_name",
        additional_project_context="additional_project_context",
        capture_start_date=datetime.utcnow,
        capture_end_date=datetime.utcnow,
        request_dataset=request_dataset,
        cost="cost",
        spatial_extent=json.dumps(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [10.0, 10.0],
                        [10.31, 10.0],
                        [10.31, 10.44],
                        [10.0, 10.44],
                        [10.0, 10.0],
                    ]
                ],
            }
        ),
        spatial_resolution="EPSG:4326",
        data_capture_urgency="data_capture_urgency",
        additional_information="additional_information",
        request_date=datetime.utcnow,
        submission_date=datetime.utcnow,
    )
]
