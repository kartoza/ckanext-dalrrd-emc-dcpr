import logging
import typing

from ckan.plugins import toolkit
from ckan.lib.navl.dictization_functions import (
    Missing,
)  # note: imported for type hints only

from ..constants import DcprRequestModerationAction

logger = logging.getLogger(__name__)


def dcpr_moderation_choices_validator(value: str):
    choices = [
        DcprRequestModerationAction.APPROVE.value,
        DcprRequestModerationAction.REJECT.value,
        DcprRequestModerationAction.REQUEST_CLARIFICATION.value,
    ]
    if value not in choices:
        raise toolkit.Invalid(toolkit._(f"Value must be one of {', '.join(choices)}"))
    return value


def dcpr_end_date_after_start_date_validator(key, flattened_data, errors, context):
    """Validator that checks that start and end dates are consistent"""
    logger.debug(f"{flattened_data=}")


def emc_value_or_true_validator(value: typing.Union[str, Missing]):
    """Validator that provides a default value of `True` when the input is None.

    This was designed with a package's `private` field in mind. We want it to be
    assigned a value of True when it is not explicitly provided on package creation.
    This shall enforce creating private packages by default.

    """

    logger.debug(f"inside value_or_true. Original value: {value!r}")
    return value if value != toolkit.missing else True


def emc_srs_validator(value: str) -> str:
    """Validator for a dataset's spatial_reference_system field"""

    try:
        parsed_value = value.replace(" ", "").upper()
        if parsed_value.count(":") == 0:
            raise toolkit.Invalid(
                toolkit._("Please provide a colon-separated value, e.g. EPSG:4326")
            )
    except AttributeError:
        value = "EPSG:4326"

    try:
        authority, code = value.split(":")
    except ValueError:
        raise toolkit.Invalid(
            toolkit._(
                "Could not extract Spatial Reference System's authority and code. "
                "Please provide them as a colon-separated value, e.g. "
                "EPSG:4326"
            )
            % {"value": value}
        )

    return value
