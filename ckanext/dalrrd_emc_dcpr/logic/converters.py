import json
import logging
from copy import deepcopy
from ckan.plugins import toolkit
from ckan.common import _
import ckan.lib.navl.dictization_functions as df

Invalid = df.Invalid


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

    except (AttributeError, TypeError):
        if value == "" or not isinstance(value, str):
            value = "-22.1265, 16.4699, -34.8212, 32.8931"
        values = value.split(",")
        bbox_coords = [float(i) for i in values]
        upper_lat = bbox_coords[0]
        left_lon = bbox_coords[1]
        lower_lat = bbox_coords[2]
        right_lon = bbox_coords[3]

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


def convert_choices_select_to_int(data_dict, context):
    """
    while submitting the select choices numerical
    values, they are returned as strings,
    they should be submitted as ints, otherwises
    a value error would be raised.
    """
    # TODO: adding the field name for proper loggin

    logger.debug("convert select choices to int ")
    if data_dict == "":
        return ""
    try:
        return int(data_dict)
    except:
        raise toolkit.Invalid("select field should have a string value")


def check_if_number(data_dict):
    """
    check if the given value can be
    converted to a number
    """
    logger.debug("convert to real number ")
    if data_dict == "":
        return ""
    try:
        return float(data_dict)
    except:
        raise toolkit.Invalid("select field should be a number ")


def check_if_int(data_dict):
    """
    check if the given value can be
    converted to an integer
    """
    logger.debug("convert to int ")
    if data_dict == "":
        return ""
    try:
        return int(data_dict)
    except:
        raise toolkit.Invalid("select field should be an integer ")


def convert_select_custom_choice_to_extra(data_dict):
    """
    adding custom field to select options,
    currently appears as "__extras" in the
    database,
    """
    return data_dict


def default_metadata_standard_name(value):
    """
    returns SANS1878 as the default
    metadata standard name.
    """
    if value == "":
        return "SANS 1878-1:2011"


def default_metadata_standard_version(value):
    """
    returns SANS1878 as the default
    metadata standard name.
    """
    if value == "":
        return "1.1"


def flatten_resource_repeated_field(data_dict):
    distribution_fields = {
        "distribution_offline_source-0-density": "offline_source_density",
        "distribution_offline_source-0-density_units": "offline_source_density_units",
        "distribution_offline_source-0-medium_formats": "offline_source_medium_formats",
        "distribution_offline_source-0-medium_notes": "offline_source_medium_notes",
        "distribution_offline_source-0-name": "offline_source_name",
        "distribution_offline_source-0-volumes": "offline_source_volumes",
    }
    resources = data_dict.get("resources")
    if len(resources) > 0:
        for res in resources:
            for i in distribution_fields:  # bad with great inputs which is not expected
                try:
                    val = deepcopy(res[i])
                    del res[i]
                    res[distribution_fields[i]] = val
                except:
                    pass
    raise RuntimeError(resources)
