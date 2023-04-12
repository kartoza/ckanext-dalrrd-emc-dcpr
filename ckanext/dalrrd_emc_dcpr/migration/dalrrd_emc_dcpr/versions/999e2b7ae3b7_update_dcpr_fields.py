"""update dcpr fields

Revision ID: 999e2b7ae3b7
Revises: fbd4fb40d15c
Create Date: 2023-04-10 09:23:15.601228

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Text


# revision identifiers, used by Alembic.
revision = "999e2b7ae3b7"
down_revision = "fbd4fb40d15c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "dcpr_request", Column("organisation_role", Text(), default="originator")
    )


def downgrade():
    op.drop_column("dcpr_request", "organisation_role")
