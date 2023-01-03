"""empty message

Revision ID: 9880e2b398a4
Revises: e996e739c44c
Create Date: 2022-12-11 17:37:52.955408

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, types, Table, ForeignKey
import datetime
from ckan import model

# revision identifiers, used by Alembic.
revision = "9880e2b398a4"
down_revision = "e996e739c44c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "saved_searches",
        model.meta.metadata,
        sa.Column(
            "saved_search_id",
            types.UnicodeText,
            primary_key=True,
            default=model.types.make_uuid,
        ),
        sa.Column(
            "owner_user",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column(
            "search_query",
            types.UnicodeText,
        ),
        sa.Column(
            "saved_search_title",
            types.UnicodeText,
        ),
        sa.Column(
            "saved_search_date", types.DateTime, default=datetime.datetime.utcnow
        ),
    )


def downgrade():
    op.drop_table("saved_searches")
