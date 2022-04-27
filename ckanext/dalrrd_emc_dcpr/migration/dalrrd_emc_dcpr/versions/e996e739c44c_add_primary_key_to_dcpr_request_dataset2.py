"""add-primary-key-to-dcpr-request-dataset2

Revision ID: e996e739c44c
Revises: f32628e99b38
Create Date: 2022-04-27 11:21:20.256011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e996e739c44c"
down_revision = "f32628e99b38"
branch_labels = None
depends_on = None

_TABLE_NAME = "dcpr_request_dataset"


def upgrade():
    op.create_primary_key(
        f"pk_{_TABLE_NAME}", table_name=_TABLE_NAME, columns=["dataset_id"]
    )


def downgrade():
    pass
