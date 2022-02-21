import pytest

from ckanext.dalrrd_emc_dcpr.logic import converters

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "10, 0, 0, 10",
            '{"type": "Polygon", "coordinates": [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]}',
        ),
    ],
)
def test_emc_bbox_validator(value, expected):
    assert converters.emc_bbox_converter(value) == expected
