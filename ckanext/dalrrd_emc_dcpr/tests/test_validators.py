import pytest
from ckan.lib.navl.dictization_functions import missing

from ..plugin import value_or_true_validator

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
    result = value_or_true_validator(value)
    assert result == expected
