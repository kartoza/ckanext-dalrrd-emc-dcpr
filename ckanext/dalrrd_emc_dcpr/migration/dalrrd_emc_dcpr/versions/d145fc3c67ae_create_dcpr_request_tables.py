"""create dcpr request tables

Revision ID: 1c1f04f6c0ab
Revises:
Create Date: 2022-02-24 08:13:52.115714

"""
import datetime as dt

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, types, Table, ForeignKey
from ckan.model import core, domain_object, meta, types as _types

# revision identifiers, used by Alembic.
revision = "d145fc3c67ae"
down_revision = None
branch_labels = ("dalrrd_emc_dcpr",)
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
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column(
            "csi_moderator",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column(
            "nsif_reviewer",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column("status", types.UnicodeText),
        sa.Column("organization_name", types.UnicodeText),
        sa.Column("organization_level", types.UnicodeText),
        sa.Column("organization_address", types.UnicodeText),
        sa.Column("proposed_project_name", types.UnicodeText),
        sa.Column("additional_project_context", types.UnicodeText),
        sa.Column("capture_start_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("capture_end_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("cost", types.UnicodeText),
        sa.Column("spatial_extent", types.UnicodeText),
        sa.Column("spatial_resolution", types.UnicodeText),
        sa.Column("data_capture_urgency", types.UnicodeText),
        sa.Column("additional_information", types.UnicodeText),
        sa.Column("additional_documents", types.UnicodeText),
        sa.Column("request_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("submission_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("nsif_review_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("nsif_recommendation", types.UnicodeText),
        sa.Column("nsif_review_notes", types.UnicodeText),
        sa.Column("nsif_review_additional_documents", types.UnicodeText),
        sa.Column("csi_moderation_notes", types.UnicodeText),
        sa.Column("csi_moderation_additional_documents", types.UnicodeText),
        sa.Column("csi_moderation_date", types.DateTime, default=dt.datetime.utcnow),
    )

    op.create_table(
        "dcpr_request_dataset",
        meta.metadata,
        sa.Column(
            "dcpr_request_id",
            types.UnicodeText,
            ForeignKey("dcpr_request.csi_reference_id"),
            primary_key=True,
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
        sa.Column(
            "target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid
        ),
        sa.Column(
            "dcpr_request_id",
            types.UnicodeText,
            ForeignKey("dcpr_request.csi_reference_id"),
        ),
        sa.Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
        sa.Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
    )

    op.create_table(
        "dcpr_geospatial_request",
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
            "nsif_reviewer",
            types.UnicodeText,
            ForeignKey("user.id"),
            nullable=False,
        ),
        sa.Column("status", types.UnicodeText),
        sa.Column("organization_name", types.UnicodeText),
        sa.Column("dataset_purpose", types.UnicodeText),
        sa.Column("interest_region", types.UnicodeText),
        sa.Column("resolution_scale", types.UnicodeText),
        sa.Column("additional_information", types.UnicodeText),
        sa.Column("request_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("submission_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("nsif_review_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("nsif_review_notes", types.UnicodeText),
        sa.Column("nsif_review_additional_documents", types.UnicodeText),
        sa.Column("csi_moderation_notes", types.UnicodeText),
        sa.Column("csi_review_additional_documents", types.UnicodeText),
        sa.Column("csi_moderation_date", types.DateTime, default=dt.datetime.utcnow),
        sa.Column("dataset_sasdi_category", types.UnicodeText),
        sa.Column("custodian_organization", types.UnicodeText),
        sa.Column("data_type", types.UnicodeText),
    )

    op.create_table(
        "dcpr_geospatial_request_notification",
        meta.metadata,
        sa.Column(
            "target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid
        ),
        sa.Column(
            "dcpr_geospatial_request_id",
            types.UnicodeText,
            ForeignKey("dcpr_geospatial_request.csi_reference_id"),
        ),
        sa.Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
        sa.Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
    )


def downgrade():
    op.drop_table("dcpr_geospatial_request_notification")
    op.drop_table("dcpr_geospatial_request")

    op.drop_table("dcpr_request_dataset")
    op.drop_table("dcpr_request_notification")
    op.drop_table("dcpr_request")
