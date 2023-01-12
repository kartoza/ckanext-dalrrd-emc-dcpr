"""create error reports tables

Revision ID: e4f399857598
Revises: e996e739c44c
Create Date: 2022-09-21 11:18:36.193379

"""
import datetime as dt

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, types, Table, ForeignKey
from ckan.model import core, domain_object, meta, types as _types


# revision identifiers, used by Alembic.
revision = "e4f399857598"
down_revision = "e996e739c44c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "error_report",
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
            "nsif_reviewer",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=True,
        ),
        sa.Column(
            "metadata_record",
            types.UnicodeText,
            ForeignKey("package.id"),
            nullable=False,
        ),
        sa.Column("status", types.UnicodeText),
        sa.Column("error_application", types.UnicodeText),
        sa.Column("error_description", types.UnicodeText, nullable=False),
        sa.Column("solution_description", types.UnicodeText),
        sa.Column("request_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("nsif_moderation_notes", types.UnicodeText),
        sa.Column("nsif_review_additional_documents", types.UnicodeText),
        sa.Column("nsif_moderation_date", types.DateTime),
    )

    op.create_table(
        "error_report_notification",
        meta.metadata,
        sa.Column(
            "target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid
        ),
        sa.Column(
            "error_report_id",
            types.UnicodeText,
            ForeignKey("error_report.csi_reference_id"),
        ),
        sa.Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
        sa.Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
    )
    #
    # # remove the old error reports tables
    # op.drop_table("dcpr_error_report_notification")
    # op.drop_table("dcpr_error_report")


def downgrade():
    op.drop_table("error_report_notification")
    op.drop_table("error_report")
