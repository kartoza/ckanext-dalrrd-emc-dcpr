import json
import typing
from datetime import datetime

from . import (
    _CkanBootstrapDCPRRequest,
    _CkanBootstrapEmcDataset
)

SAMPLE_REQUESTS: typing.Final[typing.List[_CkanBootstrapDCPRRequest]] = [
    _CkanBootstrapDCPRRequest(
        status="status",
        organization_name="organization_name",
        organization_level="organization_level",
        organization_address="organization_address",
        proposed_project_name="proposed_project_name",
        additional_project_context="additional_project_context",
        capture_start_date=datetime.datetime.utcnow,
        capture_end_date=datetime.datetime.utcnow,
        request_dataset=[
            _CkanBootstrapEmcDataset()
        ],
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
        request_date=datetime.datetime.utcnow,
        submission_date=datetime.datetime.utcnow,

    )
]
