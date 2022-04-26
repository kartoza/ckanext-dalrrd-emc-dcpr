"""add-organization-to-dcpr_request

Revision ID: eee6ee98d479
Revises: 944abb28b65b
Create Date: 2022-04-26 18:01:02.288250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eee6ee98d479"
down_revision = "944abb28b65b"
branch_labels = None
depends_on = None

_TABLE_NAME = "dcpr_request"


def upgrade():
    op.add_column(
        _TABLE_NAME,
        sa.Column(
            "organization_id",
            sa.types.UnicodeText,
            sa.ForeignKey("group.id"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column(
        _TABLE_NAME,
        "organization_id",
    )
