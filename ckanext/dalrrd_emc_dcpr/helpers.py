import json
import logging
import typing

from shapely import geometry
from ckan.plugins import toolkit

from . import constants
from .logic.action.emc import show_version

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


def helper_show_version(*args, **kwargs) -> typing.Dict:
    return show_version()


def user_is_org_member(
    org_id: str, user=None, role: typing.Optional[str] = None
) -> bool:
    """Check if user has editor role in the input organization."""
    logger.debug(f"{locals()=}")
    result = False
    if user is not None:
        member_list_action = toolkit.get_action("member_list")
        org_members = member_list_action(
            data_dict={"id": org_id, "object_type": "user"}
        )
        logger.debug(f"{user.id=}")
        logger.debug(f"{org_members=}")
        for member_id, _, member_role in org_members:
            if user.id == member_id:
                if role is None or member_role.lower() == role.lower():
                    result = True
                break
    return result


def _pad_geospatial_extent(extent: typing.Dict, padding: float) -> typing.Dict:
    geom = geometry.shape(extent)
    padded = geom.buffer(padding, join_style=geometry.JOIN_STYLE.mitre)
    oriented_padded = geometry.polygon.orient(padded)
    return geometry.mapping(oriented_padded)
