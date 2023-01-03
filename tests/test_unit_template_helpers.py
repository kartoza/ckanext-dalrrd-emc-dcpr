import json
from unittest import mock

import pytest
from shapely import geometry

from ckanext.dalrrd_emc_dcpr import helpers

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "coords, padding, expected_geom",
    [
        pytest.param(
            [
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
                [0, 0],
            ],
            0.1,
            geometry.Polygon(
                (
                    (-0.1, -0.1),
                    (1.1, -0.1),
                    (1.1, 1.1),
                    (-0.1, 1.1),
                    (-0.1, -0.1),
                )
            ),
        ),
        pytest.param(
            [
                [16.4699, -46.9657],
                [37.9777, -46.9657],
                [37.9777, -22.1265],
                [16.4699, -22.1265],
                [16.4699, -46.9657],
            ],
            1,
            geometry.Polygon(
                (
                    (15.4699, -47.9657),
                    (38.9777, -47.9657),
                    (38.9777, -21.1265),
                    (15.4699, -21.1265),
                    (15.4699, -47.9657),
                )
            ),
        ),
    ],
)
def test_pad_geospatial_extent(coords, padding, expected_geom):
    result = helpers._pad_geospatial_extent(
        {"type": "Polygon", "coordinates": [coords]}, padding
    )
    result_geom = geometry.shape(result)
    print(f"result_geom: {result_geom}")
    assert result_geom.almost_equals(expected_geom, 6)


@pytest.mark.parametrize(
    "coords, padding, expected",
    [
        pytest.param(
            [
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
                [0, 0],
            ],
            None,
            geometry.Polygon(
                (
                    (0, 0),
                    (1, 0),
                    (1, 1),
                    (0, 1),
                    (0, 0),
                )
            ),
        ),
    ],
)
def test_get_default_spatial_search_extent(
    app, ckan_config, monkeypatch, coords, padding, expected
):
    extent = json.dumps({"type": "Polygon", "coordinates": [coords]})
    with app.flask_app.app_context():
        monkeypatch.setitem(
            ckan_config, "ckan.dalrrd_emc_dcpr.default_spatial_search_extent", extent
        )
        result = helpers.get_default_spatial_search_extent(padding_degrees=padding)
        result_geom = geometry.shape(json.loads(result))
        assert result_geom.almost_equals(expected)
