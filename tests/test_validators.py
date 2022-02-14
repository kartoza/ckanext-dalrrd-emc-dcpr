import pytest
from ckan.lib.navl.dictization_functions import missing

from ckanext.dalrrd_emc_dcpr.logic import validators

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value, expected",
    [
        (missing, True),
        ("something", "something"),
        (30, 30),
        (2.345, 2.345),
        ("", ""),
        (None, None),
    ],
)
def test_value_or_true_validator(value, expected):
    result = validators.emc_value_or_true_validator(value)
    assert result == expected
