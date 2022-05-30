"""make-dcpr-request-dataset-fields-mandatory

Revision ID: f803c445a6d6
Revises: 4023da55bff3
Create Date: 2022-04-27 09:53:25.806370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f803c445a6d6"
down_revision = "4023da55bff3"
branch_labels = None
depends_on = None

_TABLE_NAME = "dcpr_request_dataset"


def upgrade():
    op.alter_column(_TABLE_NAME, "proposed_dataset_title", nullable=False)
    op.alter_column(_TABLE_NAME, "dataset_purpose", nullable=False)


def downgrade():
    op.alter_column(_TABLE_NAME, "proposed_dataset_title", nullable=True)
    op.alter_column(_TABLE_NAME, "dataset_purpose", nullable=True)
