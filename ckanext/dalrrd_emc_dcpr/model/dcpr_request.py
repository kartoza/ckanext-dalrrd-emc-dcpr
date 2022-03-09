import datetime
from typing import Optional

from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey

from ckan.model import core, domain_object, meta, types as _types, Session

dcpr_request_table = Table(
    "dcpr_request",
    meta.metadata,
    Column(
        "csi_reference_id",
        types.UnicodeText,
        primary_key=True,
        default=_types.make_uuid,
    ),
    Column(
        "owner_user",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    ),
    Column(
        "csi_moderator",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    ),
    Column(
        "nsif_reviewer",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    ),
    Column("status", types.UnicodeText),
    Column("organization_name", types.UnicodeText),
    Column("organization_level", types.UnicodeText),
    Column("organization_address", types.UnicodeText),
    Column("proposed_project_name", types.UnicodeText),
    Column("additional_project_context", types.UnicodeText),
    Column("capture_start_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("capture_end_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("cost", types.UnicodeText),
    Column("spatial_extent", types.UnicodeText),
    Column("spatial_resolution", types.UnicodeText),
    Column("data_capture_urgency", types.UnicodeText),
    Column("additional_information", types.UnicodeText),
    Column("additional_documents", types.UnicodeText),
    Column("request_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("submission_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("nsif_review_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("nsif_recommendation", types.UnicodeText),
    Column("nsif_review_notes", types.UnicodeText),
    Column("nsif_review_additional_documents", types.UnicodeText),
    Column("csi_moderation_notes", types.UnicodeText),
    Column("csi_moderation_additional_documents", types.UnicodeText),
    Column("csi_moderation_date", types.DateTime, default=datetime.datetime.utcnow),
)

dcpr_request_dataset_table = Table(
    "dcpr_request_dataset",
    meta.metadata,
    Column("request_id", ForeignKey("dcpr_request.csi_reference_id"), primary_key=True),
    Column("dataset_custodian", types.Boolean, default=False),
    Column("data_type", types.UnicodeText),
    Column("purposed_dataset_title", types.UnicodeText),
    Column("purposed_abstract", types.UnicodeText),
    Column("dataset_purpose", types.UnicodeText),
    Column("lineage_statement", types.UnicodeText),
    Column("associated_attributes", types.UnicodeText),
    Column("feature_description", types.UnicodeText),
    Column("data_usage_restrictions", types.UnicodeText),
    Column("capture_method", types.UnicodeText),
    Column("capture_method_detail", types.UnicodeText),
)

dcpr_request_notification_table = Table(
    "dcpr_request_notification",
    meta.metadata,
    Column("target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column("request_id", types.UnicodeText, ForeignKey("dcpr_request.csi_reference_id")),
    Column("user_id", types.UnicodeText, ForeignKey("user.id")),
    Column("group_id", types.UnicodeText, ForeignKey("group.id")),
)


class DCPRRequestDataset(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, request=None, request_id=None):
        super(DCPRRequestDataset, self).__init__(request, request_id)
        self.request = request
        self.request_id = request_id

    @classmethod
    def get(cls, **kw) -> Optional["DCPRRequestDataset"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRRequest(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(DCPRRequest, self).__init__(**kw)
        self.csi_reference_id = kw.get("csi_reference_id", None)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRRequest"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    def get_dataset_elements(self) -> Optional[DCPRRequestDataset]:
        dataset = (
            meta.Session.query(DCPRRequest)
            .join(DCPRRequestDataset,
                  DCPRRequestDataset.request_id == DCPRRequest.csi_reference_id)
            .filter(DCPRRequestDataset.request_id == str(self.csi_reference))
            .all()
        )

        return dataset


class DCPRRequestNotificationTarget(domain_object.DomainObject):
    pass


def init_request_tables():
    if not dcpr_request_table.exists():
        log.debug("Creating DCPR request table")
        dcpr_request_table.create()
    else:
        log.debug("DCPR request table already exists")
    if not dcpr_request_dataset_table.exists():
        log.debug("Creating DCPR request dataset table")
        dcpr_request_dataset_table.create()
    else:
        log.debug("DCPR request dataset table already exists")
    if not dcpr_request_notification_table.exists():
        log.debug("Creating DCPR request notification target table")
        dcpr_request_notification_table.create()
    else:
        log.debug("DCPR request notification target table already exists")


meta.mapper(DCPRRequest, dcpr_request_table)
meta.mapper(DCPRRequestNotificationTarget, dcpr_request_notification_table)
meta.mapper(DCPRRequestDataset, dcpr_request_dataset_table)
