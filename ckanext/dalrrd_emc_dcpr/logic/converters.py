import json
import logging

from ckan.plugins import toolkit

logger = logging.getLogger(__name__)


def emc_bbox_converter(value: str) -> str:
    error_msg = toolkit._(
        "Invalid bounding box. Please provide a comma-separated list of values "
        "with upper left lat, upper left lon, lower right lat, lower right lon."
    )
    logger.debug(f"inside emc_bbox_converter {value=}")
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
    logger.debug(f"{parsed=}")
    return json.dumps(parsed)
