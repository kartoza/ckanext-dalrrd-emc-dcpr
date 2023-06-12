"""dcpr dataset sans fields

Revision ID: 85d073cfdf08
Revises: 999e2b7ae3b7
Create Date: 2023-04-10 14:47:59.977479

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Text

# revision identifiers, used by Alembic.
revision = "85d073cfdf08"
down_revision = "999e2b7ae3b7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "dcpr_request_dataset", Column("metadata_contact_organisation", Text())
    ),
    op.add_column("dcpr_request_dataset", Column("metadata_contact_name", Text())),
    op.add_column(
        "dcpr_request_dataset", Column("dataset_distribution_format_name", Text())
    ),
    op.add_column(
        "dcpr_request_dataset", Column("dataset_distribution_format_version", Text())
    )


def downgrade():
    op.drop_column("dcpr_request_dataset", "metadata_contact_organisation"),
    op.drop_column("dcpr_request_dataset", "metadata_contact_name"),
    op.drop_column("dcpr_request_dataset", "dataset_distribution_format_name"),
    op.drop_column("dcpr_request_dataset", "dataset_distribution_format_version")
