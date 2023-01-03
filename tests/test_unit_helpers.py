import pytest

from ckanext.dalrrd_emc_dcpr import helpers

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
                ],
            },
            # this is the expected value
            [10.0, 0.0, 0.0, 10.0],
        ),
    ],
)
def test_convert_geojson_to_bbox(value, expected):
    assert helpers.convert_geojson_to_bbox(value) == expected
