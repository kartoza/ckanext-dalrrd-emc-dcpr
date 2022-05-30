"""modify-dates-and-nullability-of-moderators

Revision ID: 944abb28b65b
Revises: a794534e0216
Create Date: 2022-04-20 10:24:10.781563

"""
import datetime as dt

from alembic import op


# revision identifiers, used by Alembic.
revision = "944abb28b65b"
down_revision = "a794534e0216"
branch_labels = None
depends_on = None

_DCPR_REQUEST_TABLE = "dcpr_request"
_DCPR_REQUEST_DATASET_TABLE = "dcpr_request_dataset"


def upgrade():
    op.alter_column(_DCPR_REQUEST_TABLE, "csi_moderator", nullable=True)
    op.alter_column(_DCPR_REQUEST_TABLE, "nsif_reviewer", nullable=True)
    op.alter_column(_DCPR_REQUEST_TABLE, "capture_start_date", server_default=None)
    op.alter_column(_DCPR_REQUEST_TABLE, "capture_end_date", server_default=None)
    op.alter_column(_DCPR_REQUEST_TABLE, "submission_date", server_default=None)
    op.alter_column(_DCPR_REQUEST_TABLE, "nsif_review_date", server_default=None)
    op.alter_column(_DCPR_REQUEST_TABLE, "csi_moderation_date", server_default=None)
    op.alter_column(
        _DCPR_REQUEST_DATASET_TABLE,
        "purposed_dataset_title",
        new_column_name="proposed_dataset_title",
    )
    op.alter_column(
        _DCPR_REQUEST_DATASET_TABLE,
        "purposed_abstract",
        new_column_name="proposed_abstract",
    )


def downgrade():
    op.alter_column(_DCPR_REQUEST_TABLE, "csi_moderator", nullable=False)
    op.alter_column(_DCPR_REQUEST_TABLE, "nsif_reviewer", nullable=False)
    op.alter_column(
        _DCPR_REQUEST_TABLE, "capture_start_date", server_default=dt.datetime.utcnow
    )
    op.alter_column(
        _DCPR_REQUEST_TABLE, "capture_end_date", server_default=dt.datetime.utcnow
    )
    op.alter_column(
        _DCPR_REQUEST_TABLE, "submission_date", server_default=dt.datetime.utcnow
    )
    op.alter_column(
        _DCPR_REQUEST_TABLE, "nsif_review_date", server_default=dt.datetime.utcnow
    )
    op.alter_column(
        _DCPR_REQUEST_TABLE, "csi_moderation_date", server_default=dt.datetime.utcnow
    )
    op.alter_column(
        _DCPR_REQUEST_DATASET_TABLE,
        "proposed_dataset_title",
        new_column_name="purposed_dataset_title",
    )
    op.alter_column(
        _DCPR_REQUEST_DATASET_TABLE,
        "proposed_abstract",
        new_column_name="purposed_abstract",
    )
