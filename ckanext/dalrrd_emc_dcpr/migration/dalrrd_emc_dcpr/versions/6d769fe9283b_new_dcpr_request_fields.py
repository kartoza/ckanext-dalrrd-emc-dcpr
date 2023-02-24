"""new dcpr request fields

Revision ID: 6d769fe9283b
Revises: 5d6f06036f61
Create Date: 2023-02-16 00:51:09.218670

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Text

# revision identifiers, used by Alembic.
revision = "6d769fe9283b"
down_revision = "5d6f06036f61"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dcpr_request", Column("organisation_level", Text())),

    op.add_column("dcpr_request", Column("organisation_address", Text())),

    op.add_column("dcpr_request", Column("contact_person_name", Text())),

    op.add_column("dcpr_request", Column("contact_person_designation", Text())),

    op.add_column("dcpr_request", Column("contact_person_email_address", Text())),

    op.add_column("dcpr_request", Column("dcpr_contact_person_phone", Text())),

    op.add_column("dcpr_request", Column("dcpr_contact_person_fax_number", Text()))


def downgrade():
    op.drop_column("dcpr_request", "organisation_level"),

    op.drop_column("dcpr_request", "organisation_address"),

    op.drop_column("dcpr_request", "contact_person_name"),

    op.drop_column("dcpr_request", "contact_person_designation"),

    op.drop_column("dcpr_request", "contact_person_email_address"),

    op.drop_column("dcpr_request", "dcpr_contact_person_phone"),

    op.drop_column("dcpr_request", "dcpr_contact_person_fax_number")
