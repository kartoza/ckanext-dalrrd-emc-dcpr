"""create dcpr request tables

Revision ID: 1c1f04f6c0ab
Revises:
Create Date: 2022-02-24 08:13:52.115714

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy import orm, types, Table, ForeignKey
from ckan.model import core, domain_object, meta, types as _types

# revision identifiers, used by Alembic.
revision = "d145fc3c67ae"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "dcpr_request",
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
            ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "csi_moderator",
            types.UnicodeText,
            ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "nsif_reviewer",
            types.UnicodeText,
            ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", types.UnicodeText),
        sa.Column("organization_name", types.UnicodeText),
        sa.Column("organization_level", types.UnicodeText),
        sa.Column("organization_address", types.UnicodeText),
        sa.Column("proposed_project_name", types.UnicodeText),
        sa.Column("additional_project_context", types.UnicodeText),
        sa.Column(
            "capture_start_date", types.DateTime, default=datetime.datetime.utcnow
        ),
        sa.Column("capture_end_date", types.DateTime, default=datetime.datetime.utcnow),
        sa.Column("cost", types.UnicodeText),
        sa.Column("spatial_extent", types.UnicodeText),
        sa.Column("spatial_resolution", types.UnicodeText),
        sa.Column("data_capture_urgency", types.UnicodeText),
        sa.Column("additional_information", types.UnicodeText),
        sa.Column("additional_documents", types.UnicodeText),
        sa.Column("request_date", types.DateTime, default=datetime.datetime.utcnow),
        sa.Column("submission_date", types.DateTime, default=datetime.datetime.utcnow),
    )

    op.create_table(
        "dcpr_request_dataset",
        meta.metadata,
        sa.Column(
            "request_id", ForeignKey("dcpr_request.csi_reference_id"), primary_key=True
        ),
        sa.Column("dataset_custodian", types.Boolean, default=False),
        sa.Column("data_type", types.UnicodeText),
        sa.Column("purposed_dataset_title", types.UnicodeText),
        sa.Column("purposed_abstract", types.UnicodeText),
        sa.Column("dataset_purpose", types.UnicodeText),
        sa.Column("lineage_statement", types.UnicodeText),
        sa.Column("associated_attributes", types.UnicodeText),
        sa.Column("feature_description", types.UnicodeText),
        sa.Column("data_usage_restrictions", types.UnicodeText),
        sa.Column("capture_method", types.UnicodeText),
        sa.Column("capture_method_detail", types.UnicodeText),
    )

    op.create_table(
        "dcpr_request_notification",
        meta.metadata,
        sa.Column("target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid),
        sa.Column("request_id", ForeignKey("dcpr_request.csi_reference_id")),
        sa.Column("user_id", ForeignKey("user.id")),
        sa.Column("group_id", ForeignKey("group.id")),
    )


def downgrade():
    op.drop_table("dcpr_request")
    op.drop_table("dcpr_request_dataset")
    op.drop_table("dcpr_request_notification")
