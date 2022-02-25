import datetime
from typing import Optional

from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey
from sqlalchemy.sql.expression import or_

from ckan.model import core, domain_object, meta, types as _types, Session

request_table = Table(
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
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "csi_moderator",
        types.UnicodeText,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "nsif_reviewer",
        types.UnicodeText,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
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
)

request_notification_target_table = Table(
    "notification_target",
    meta.metadata,
    Column("target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column("request_id", ForeignKey("dcpr_request.csi_reference_id")),
    Column("user_id", ForeignKey("user.id")),
    Column("group_id", ForeignKey("group.id")),
)

request_dataset_table = Table(
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


class Request(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(Request, self).__init__(**kw)

    @classmethod
    def get(cls, reference: Optional[str]) -> Optional["Request"]:
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(or_(cls.name == reference, cls.id == reference))
        return query.first()


class RequestNotificationTarget(domain_object.DomainObject):
    pass


class RequestDataset(domain_object.DomainObject):
    pass


def init_request_tables():
    meta.mapper(Request, request_table)
    meta.mapper(RequestNotificationTarget, request_notification_target_table)

    meta.mapper(RequestDataset, request_dataset_table)

    if not request_table.exists():
        log.debug("Creating DCPR request table")
        request_table.create()
    else:
        log.debug("DCPR request table already exists")
    if not request_dataset_table.exists():
        log.debug("Creating DCPR request dataset table")
        request_dataset_table.create()
    else:
        log.debug("DCPR request dataset table already exists")
    if not request_notification_target_table.exists():
        log.debug("Creating DCPR request notification target table")
        request_notification_target_table.create()
    else:
        log.debug("DCPR request notification target table already exists")
