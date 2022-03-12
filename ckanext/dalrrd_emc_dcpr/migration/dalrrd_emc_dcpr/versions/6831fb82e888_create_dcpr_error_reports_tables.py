"""create dcpr error reports tables

Revision ID: 6831fb82e888
Revises: d145fc3c67ae
Create Date: 2022-03-12 20:43:44.038193

"""
import datetime as dt

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, types, Table, ForeignKey
from ckan.model import core, domain_object, meta, types as _types


# revision identifiers, used by Alembic.
revision = "6831fb82e888"
down_revision = "d145fc3c67ae"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "dcpr_error_report",
        meta.metadata,
        sa.Column(
            "csi_reference_id",
            types.UnicodeText,
            primary_key=True,
            default=_types.make_uuid,
        ),
        sa.Column(
            "owner_user",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column(
            "csi_reviewer",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column(
            "metadata_record",
            types.UnicodeText,
            ForeignKey("package.id"),
            nullable=True,
        ),
        sa.Column("status", types.UnicodeText),
        sa.Column("error_application", types.UnicodeText),
        sa.Column("error_description", types.UnicodeText),
        sa.Column("solution_description", types.UnicodeText),
        sa.Column("request_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("csi_moderation_notes", types.UnicodeText),
        sa.Column("csi_review_additional_documents", types.UnicodeText),
        sa.Column("csi_moderation_date", types.DateTime, default=dt.datetime.utcnow),
    )

    op.create_table(
        "dcpr_error_report_notification",
        meta.metadata,
        sa.Column(
            "target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid
        ),
        sa.Column(
            "dcpr_error_report_id",
            types.UnicodeText,
            ForeignKey("dcpr_error_report.csi_reference_id"),
        ),
        sa.Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
        sa.Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
    )


def downgrade():
    op.drop_table("dcpr_error_report_notification")
    op.drop_table("dcpr_error_report")
