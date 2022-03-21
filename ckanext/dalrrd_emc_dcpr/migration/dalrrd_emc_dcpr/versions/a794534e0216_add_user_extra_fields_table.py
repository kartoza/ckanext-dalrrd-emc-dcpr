"""add-user-extra-fields-table

Revision ID: a794534e0216
Revises: 6831fb82e888
Create Date: 2022-03-18 18:30:52.915020

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy import types, ForeignKey
from ckan.model import core, domain_object, meta, types as ckan_types


# revision identifiers, used by Alembic.
revision = "a794534e0216"
down_revision = "6831fb82e888"
branch_labels = None
depends_on = None

_TABLE_NAME = "user_extra_fields"


def upgrade():
    op.create_table(
        _TABLE_NAME,
        meta.metadata,
        sa.Column(
            "id",
            types.UnicodeText,
            primary_key=True,
            default=ckan_types.make_uuid,
        ),
        sa.Column(
            "user_id",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column("affiliation", types.UnicodeText),
        sa.Column("professional_occupation", types.UnicodeText),
    )


def downgrade():
    op.drop_table(_TABLE_NAME)
