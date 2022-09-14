import datetime
from typing import Optional

from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey

from ckan.model import core, domain_object, meta, types as _types, Session, Package

error_report_table = Table(
    "error_report",
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
        "nsif_reviewer",
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
    Column("nsif_moderation_notes", types.UnicodeText),
    Column("nsif_review_additional_documents", types.UnicodeText),
    Column("nsif_moderation_date", types.DateTime, default=datetime.datetime.utcnow),
)

error_report_notification_table = Table(
    "error_report_notification",
    meta.metadata,
    Column("target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column(
        "error_report_id",
        types.UnicodeText,
        ForeignKey("error_report.csi_reference_id"),
    ),
    Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
    Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
)


class ErrorReportNotificationTarget(
    core.StatefulObjectMixin, domain_object.DomainObject
):
    def __init__(self, **kw):
        super(ErrorReportNotificationTarget, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["ErrorReportNotificationTarget"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class ErrorReport(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(ErrorReport, self).__init__(**kw)
        self.csi_reference_id = kw.get("csi_reference_id", None)

    @classmethod
    def get(cls, **kw) -> Optional["ErrorReport"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    def get_notification_targets(self) -> Optional[ErrorReportNotificationTarget]:
        targets = (
            meta.Session.query(ErrorReport)
            .join(
                ErrorReportNotificationTarget,
                ErrorReportNotificationTarget.error_report_id
                == ErrorReport.csi_reference_id,
            )
            .filter(
                ErrorReportNotificationTarget.error_report_id
                == str(self.csi_reference)
            )
            .all()
        )

        return targets

    def get_metadata_record(self) -> Optional[Package]:
        record = (
            meta.Session.query(ErrorReport)
            .join(
                Package,
                Package.id == ErrorReport.metadata_record,
            )
            .first()
        )

        return record


meta.mapper(ErrorReport, error_report_table)
meta.mapper(ErrorReportNotificationTarget, error_report_notification_table)
