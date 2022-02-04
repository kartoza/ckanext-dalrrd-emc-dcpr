import logging
import typing

from ckan.plugins import toolkit
from ckan.lib.navl.dictization_functions import (
    Missing,
)  # note: imported for type hints only

logger = logging.getLogger(__name__)


def emc_value_or_true_validator(value: typing.Union[str, Missing]):
    """Validator that provides a default value of `True` when the input is None.

    This was designed with a package's `private` field in mind. We want it to be
    assigned a value of True when it is not explicitly provided on package creation.
    This shall enforce creating private packages by default.

    """

    logger.debug(f"inside value_or_true. Original value: {value!r}")
    return value if value != toolkit.missing else True
