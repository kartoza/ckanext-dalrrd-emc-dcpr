"""remove-extraneous-org-columns-from-dcpr-request

Revision ID: 4023da55bff3
Revises: eee6ee98d479
Create Date: 2022-04-26 18:06:51.382819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4023da55bff3"
down_revision = "eee6ee98d479"
branch_labels = None
depends_on = None

_TABLE_NAME = "dcpr_request"


def upgrade():
    op.drop_column(_TABLE_NAME, "organization_name")
    op.drop_column(_TABLE_NAME, "organization_level")
    op.drop_column(_TABLE_NAME, "organization_address")


def downgrade():
    op.add_column(
        _TABLE_NAME,
        sa.Column("organization_name", sa.types.UnicodeText),
    )
    op.add_column(
        _TABLE_NAME,
        sa.Column("organization_level", sa.types.UnicodeText),
    )
    op.add_column(
        _TABLE_NAME,
        sa.Column("organization_address", sa.types.UnicodeText),
    )
