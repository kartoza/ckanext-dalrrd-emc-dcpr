import datetime as dt
import json
import random
import typing
from itertools import count

from ckan.plugins import toolkit

from ..constants import ISO_TOPIC_CATEGORIES
from . import (
    _CkanEmcDataset,
    _CkanResource,
)

SAMPLE_DATASET_TAG = "sample-data"


def generate_sample_datasets(
    num_datasets: int,
    name_prefix: str,
    owner_org: str,
    name_suffix: typing.Optional[str] = None,
    temporal_range_start: dt.datetime = dt.datetime(2021, 1, 1),
    temporal_range_end: dt.datetime = dt.datetime(2022, 12, 31),
    latitude_range_start: float = -35,
    latitude_range_end: float = -21,
    longitude_range_start: float = 16.3,
    longitude_range_end: float = 33,
) -> typing.Iterator[_CkanEmcDataset]:
    possible_dates = _get_days(temporal_range_start, temporal_range_end)
    sasdi_themes = [
        t
        for t in toolkit.config.get("ckan.dalrrd_emc_dcpr.sasdi_themes").splitlines()
        if t != ""
    ]
    sasdi_themes.append(None)
    for i in range(num_datasets):
        name = f"{name_prefix}-{i}{'-' + name_suffix if name_suffix else ''}"
        min_lon, max_lon, min_lat, max_lat = _get_random_temporal_extent(
            latitude_range_start,
            latitude_range_end,
            longitude_range_start,
            longitude_range_end,
        )
        yield _CkanEmcDataset(
            name=name,
            private=random.choice((True, False)),
            notes=f"Abstract for {name}",
            reference_date=random.choice(possible_dates).strftime("%Y-%m-%d"),
            iso_topic_category=ISO_TOPIC_CATEGORIES[
                random.randrange(0, len(ISO_TOPIC_CATEGORIES))
            ][0],
            sasdi_theme=random.choice(sasdi_themes),
            owner_org=owner_org,
            maintainer="Nobody, No One, Ms.",
            spatial=json.dumps(
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [min_lon, min_lat],
                            [max_lon, min_lat],
                            [max_lon, max_lat],
                            [min_lon, max_lat],
                            [min_lon, min_lat],
                        ]
                    ],
                }
            ),
            equivalent_scale=random.choice(
                ("500", "1000", "5000", "10000", "20000", "50000")
            ),
            spatial_representation_type=random.choice(
                ("001", "002", "003", "004", "007")
            ),
            spatial_reference_system=random.choice(("EPSG:4326", "EPSG:3857")),
            dataset_language="en",
            metadata_language="en",
            dataset_character_set="utf-8",
            resources=[
                _CkanResource("http://fake.com", format="shp", format_version="1")
            ],
            tags=[{"name": SAMPLE_DATASET_TAG, "vocabulary_id": None}],
        )


def _get_days(start: dt.datetime, end: dt.datetime) -> typing.List[dt.datetime]:
    result = []
    for i in count():
        current_date = start + dt.timedelta(days=i)
        if current_date <= end:
            result.append(current_date)
        else:
            break
    return result


def _get_random_temporal_extent(
    latitude_start: float = -90,
    latitude_end: float = 90,
    longitude_start: float = -180,
    longitude_end: float = 180,
) -> typing.Tuple[float, float, float, float]:
    lon_start = longitude_start + random.random() * (longitude_end - longitude_start)
    lon_end = lon_start + random.random() * (longitude_end - lon_start)
    lat_start = latitude_start + random.random() * (latitude_end - latitude_start)
    lat_end = lat_start + random.random() * (latitude_end - lat_start)
    return lon_start, lon_end, lat_start, lat_end
