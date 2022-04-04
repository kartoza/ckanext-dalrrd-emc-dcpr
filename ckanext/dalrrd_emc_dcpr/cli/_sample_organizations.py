import typing
from . import (
    _CkanBootstrapOrganization,
    _CkanBootstrapHarvester,
)

_SAMPLE_ORG_DESCRIPTION: typing.Final[str] = (
    "This is a sample organization. It is meant for aiding the development and "
    "testing purposes"
)

SAMPLE_ORGANIZATIONS: typing.Final[
    typing.List[
        typing.Tuple[
            _CkanBootstrapOrganization,
            typing.List[typing.Tuple[str, str]],
            typing.List[_CkanBootstrapHarvester],
        ]
    ]
] = [
    (
        _CkanBootstrapOrganization("Sample org 1", _SAMPLE_ORG_DESCRIPTION),
        [
            ("tester1", "member"),
            ("tester2", "editor"),
            ("tester3", "publisher"),
        ],
        [
            _CkanBootstrapHarvester(
                name="local-pycsw",
                url="http://csw-harvest-target:8000",
                source_type="csw",
                update_frequency="MANUAL",
                configuration={"default_tags": ["csw", "harvest"]},
            )
        ],
    ),
    (
        _CkanBootstrapOrganization("Sample org 2", _SAMPLE_ORG_DESCRIPTION),
        [
            ("tester4", "member"),
            ("tester5", "editor"),
            ("tester6", "publisher"),
        ],
        [],
    ),
    (
        _CkanBootstrapOrganization("NSIF", _SAMPLE_ORG_DESCRIPTION),
        [
            ("tester1", "member"),
            ("tester2", "editor"),
            ("tester3", "publisher"),
        ],
        [],
    ),
    (
        _CkanBootstrapOrganization("CSI", _SAMPLE_ORG_DESCRIPTION),
        [
            ("tester4", "member"),
            ("tester5", "editor"),
            ("tester6", "publisher"),
        ],
        [],
    ),
]
