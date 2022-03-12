import datetime
from typing import Optional

from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey

from ckan.model import core, domain_object, meta, types as _types, Session, Package

dcpr_error_report_table = Table(
    "dcpr_error_report",
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
        "csi_reviewer",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    ),
    Column(
        "metadata_record",
        types.UnicodeText,
        ForeignKey("package.id"),
        nullable=True,
    ),
    Column("status", types.UnicodeText),
    Column("error_application", types.UnicodeText),
    Column("error_description", types.UnicodeText),
    Column("solution_description", types.UnicodeText),
    Column("request_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("csi_moderation_notes", types.UnicodeText),
    Column("csi_review_additional_documents", types.UnicodeText),
    Column("csi_moderation_date", types.DateTime, default=datetime.datetime.utcnow),
)

dcpr_error_report_notification_table = Table(
    "dcpr_error_report_notification",
    meta.metadata,
    Column("target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column(
        "dcpr_error_report_id",
        types.UnicodeText,
        ForeignKey("dcpr_error_report.csi_reference_id"),
    ),
    Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
    Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
)


class DCPRErrorReportNotificationTarget(
    core.StatefulObjectMixin, domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRErrorReportNotificationTarget, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRErrorReportNotificationTarget"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRErrorReport(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(DCPRErrorReport, self).__init__(**kw)
        self.csi_reference_id = kw.get("csi_reference_id", None)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRErrorReport"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    def get_notification_targets(self) -> Optional[DCPRErrorReportNotificationTarget]:
        targets = (
            meta.Session.query(DCPRErrorReport)
            .join(
                DCPRErrorReportNotificationTarget,
                DCPRErrorReportNotificationTarget.dcpr_error_report_id
                == DCPRErrorReport.csi_reference_id,
            )
            .filter(
                DCPRErrorReportNotificationTarget.dcpr_error_report_id
                == str(self.csi_reference)
            )
            .all()
        )

        return targets

    def get_metadata_record(self) -> Optional[Package]:
        record = (
            meta.Session.query(DCPRErrorReport)
            .join(
                Package,
                Package.id == DCPRErrorReport.metadata_record,
            )
            .first()
        )

        return record


meta.mapper(DCPRErrorReport, dcpr_error_report_table)
meta.mapper(DCPRErrorReportNotificationTarget, dcpr_error_report_notification_table)
