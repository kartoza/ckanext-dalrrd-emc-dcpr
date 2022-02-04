import json
import logging
import typing

from shapely import geometry
from ckan.plugins import toolkit

from . import constants

logger = logging.getLogger(__name__)


def get_sasdi_themes(*args, **kwargs) -> typing.List[typing.Dict[str, str]]:
    logger.debug(f"inside get_sasdi_themes {args=} {kwargs=}")
    try:
        sasdi_themes = toolkit.get_action("tag_list")(
            data_dict={"vocabulary_id": constants.SASDI_THEMES_VOCABULARY_NAME}
        )
    except toolkit.ObjectNotFound:
        sasdi_themes = []
    return [{"value": t, "label": t} for t in sasdi_themes]


def get_iso_topic_categories(*args, **kwargs) -> typing.List[typing.Dict[str, str]]:
    logger.debug(f"inside get_iso_topic_categories {args=} {kwargs=}")
    return [
        {"value": cat[0], "label": cat[1]} for cat in constants.ISO_TOPIC_CATEGORIES
    ]


def get_default_spatial_search_extent(
    padding_degrees: typing.Optional[float] = None,
) -> str:
    """
    Return GeoJSON polygon with bbox to use for default view of spatial search map widget.
    """
    configured_extent = toolkit.config.get(
        "ckan.dalrrd_emc_dcpr.default_spatial_search_extent"
    )
    if padding_degrees and configured_extent:
        parsed_extent = json.loads(configured_extent)
        padded = _pad_geospatial_extent(parsed_extent, padding_degrees)
        result = json.dumps(padded)
    else:
        result = configured_extent
    return result


def _pad_geospatial_extent(extent: typing.Dict, padding: float) -> typing.Dict:
    geom = geometry.shape(extent)
    padded = geom.buffer(padding, join_style=geometry.JOIN_STYLE.mitre)
    oriented_padded = geometry.polygon.orient(padded)
    return geometry.mapping(oriented_padded)
