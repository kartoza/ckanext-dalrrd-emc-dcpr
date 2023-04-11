"""update dcpr dataset

Revision ID: fbd4fb40d15c
Revises: 6d769fe9283b
Create Date: 2023-02-19 19:12:26.734215

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Text

# revision identifiers, used by Alembic.
revision = "fbd4fb40d15c"
down_revision = "6d769fe9283b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dcpr_request_dataset", Column("topic_category", Text())),
    op.add_column("dcpr_request_dataset", Column("dataset_characterset", Text())),
    op.add_column("dcpr_request_dataset", Column("metadata_characterset", Text())),


def downgrade():
    op.drop_column("dcpr_request_dataset", Column("topic_category", Text())),
    op.drop_column("dcpr_request_dataset", Column("dataset_characterset", Text())),
    op.drop_column("dcpr_request_dataset", Column("metadata_characterset", Text())),
