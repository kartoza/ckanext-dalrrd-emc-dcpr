"""Additional fields for the user model for storing affiliation details"""

import logging

import sqlalchemy
from ckan import model
from ckan.model import types as types_
from sqlalchemy import orm

logger = logging.getLogger(__name__)

user_extra_fields_table = sqlalchemy.Table(
    "user_extra_fields",
    sqlalchemy.Column(
        "id", sqlalchemy.types.UnicodeText, primary_key=True, default=types_.make_uuid
    ),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.types.UnicodeText,
        sqlalchemy.ForeignKey("user.id"),
    ),
    sqlalchemy.Column(
        "affiliation",
        sqlalchemy.types.UnicodeText,
    ),
    sqlalchemy.Column(
        "professional_occupation",
        sqlalchemy.types.UnicodeText,
    ),
)


class UserExtraFields(model.core.StatefulObjectMixin, model.domain_object.DomainObject):
    pass


model.meta.mapper(
    UserExtraFields,
    user_extra_fields_table,
    properties={
        "user": orm.relationship(
            model.User,
            uselist=False,
            backref=orm.backref("_extra_fields", cascade="all, delete, delete-orphan"),
        ),
    },
)
