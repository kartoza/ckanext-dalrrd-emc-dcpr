"""Update error report

Revision ID: 3297b0e63432
Revises: fbd4fb40d15c
Create Date: 2024-02-07 10:45:22.796103

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Text

# revision identifiers, used by Alembic.
revision = '3297b0e63432'
down_revision = 'fbd4fb40d15c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("error_report", Column("reason_for_reject", Text(), nullable=True)),


def downgrade():
    op.drop_column("dcpr_request_dataset", Column("reason_for_reject", Text(), nullable=True)),
