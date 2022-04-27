"""add-primary-key-to-dcpr-request-dataset

Revision ID: f32628e99b38
Revises: f803c445a6d6
Create Date: 2022-04-27 10:47:15.324879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f32628e99b38"
down_revision = "f803c445a6d6"
branch_labels = None
depends_on = None

_TABLE_NAME = "dcpr_request_dataset"


def upgrade():
    op.drop_constraint("dcpr_request_dataset_pkey", _TABLE_NAME)
    op.add_column(
        _TABLE_NAME,
        sa.Column("dataset_id", sa.types.UnicodeText),
    )


def downgrade():
    pass
