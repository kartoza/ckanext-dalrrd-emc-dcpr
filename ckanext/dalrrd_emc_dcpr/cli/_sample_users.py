import typing
from . import _CkanBootstrapUser

_SAMPLE_USER_PASSWORD: typing.Final[str] = "12345678"

SAMPLE_USERS: typing.Final[typing.List[_CkanBootstrapUser]] = [
    _CkanBootstrapUser("tester1", "tester1@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester2", "tester2@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester3", "tester3@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester4", "tester4@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester5", "tester5@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester6", "tester6@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester7", "tester7@fake.mail", _SAMPLE_USER_PASSWORD),
]
