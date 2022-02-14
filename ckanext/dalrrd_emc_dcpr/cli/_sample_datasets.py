import json
import typing

from . import (
    _CkanBootstrapEmcDataset,
    _CkanBootstrapResource,
)

SAMPLE_DATASETS: typing.Final[typing.List[_CkanBootstrapEmcDataset]] = [
    _CkanBootstrapEmcDataset(
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
]
