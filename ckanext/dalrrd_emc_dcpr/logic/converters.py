import json
import logging

from ckan.plugins import toolkit

from ckan.common import _
import ckan.lib.navl.dictization_functions as df

Invalid = df.Invalid

logger = logging.getLogger(__name__)


def emc_bbox_converter(value: str) -> str:
    error_msg = toolkit._(
        "Invalid bounding box. Please provide a comma-separated list of values "
        "with upper left lat, upper left lon, lower right lat, lower right lon."
    )
    try:  # is it already a geojson?
        parsed_value = json.loads(value)
        coordinates = parsed_value["coordinates"][0]
        upper_lat = coordinates[2][1]
        left_lon = coordinates[0][0]
        lower_lat = coordinates[0][1]
        right_lon = coordinates[1][0]
    except json.JSONDecodeError:  # nope, it is a bbox
        try:
            bbox_coords = [float(i) for i in value.split(",")]
        except ValueError:
            logger.exception(msg="something failed")
            raise toolkit.Invalid(error_msg)
        else:
            upper_lat = bbox_coords[0]
            left_lon = bbox_coords[1]
            lower_lat = bbox_coords[2]
            right_lon = bbox_coords[3]
    except IndexError:
        logger.exception(msg="something failed")
        raise toolkit.Invalid(error_msg)
    parsed = {
        "type": "Polygon",
        "coordinates": [
            [
                [left_lon, lower_lat],
                [right_lon, lower_lat],
                [right_lon, upper_lat],
                [left_lon, upper_lat],
                [left_lon, lower_lat],
            ]
        ],
    }
    return json.dumps(parsed)


def spatial_resolution_converter(value: str):
    """
    the natural numbers validator used with
    spatial resolution field causes
    internal server error when the type
    is None, handled here
    """
    if value == "":
        return -1
    return value
