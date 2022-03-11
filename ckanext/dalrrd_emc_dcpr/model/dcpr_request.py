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
    Column(
        "dcpr_request_id", ForeignKey("dcpr_request.csi_reference_id"), primary_key=True
    ),
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
    Column(
        "dcpr_request_id",
        types.UnicodeText,
        ForeignKey("dcpr_request.csi_reference_id"),
    ),
    Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
    Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
)

dcpr_geospatial_request_table = Table(
    "dcpr_geospatial_request",
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
        "nsif_reviewer",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    ),
    Column("status", types.UnicodeText),
    Column("organization_name", types.UnicodeText),
    Column("dataset_purpose", types.UnicodeText),
    Column("interest_region", types.UnicodeText),
    Column("resolution_scale", types.UnicodeText),
    Column("additional_information", types.UnicodeText),
    Column("request_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("submission_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("nsif_review_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("nsif_review_notes", types.UnicodeText),
    Column("nsif_review_additional_documents", types.UnicodeText),
    Column("csi_moderation_notes", types.UnicodeText),
    Column("csi_review_additional_documents", types.UnicodeText),
    Column("csi_moderation_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("dataset_sasdi_category", types.UnicodeText),
    Column("custodian_organization", types.UnicodeText),
    Column("data_type", types.UnicodeText),
)

dcpr_geospatial_request_notification_table = Table(
    "dcpr_geospatial_request_notification",
    meta.metadata,
    Column("target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column(
        "dcpr_geospatial_request_id",
        types.UnicodeText,
        ForeignKey("dcpr_geospatial_request.csi_reference_id"),
    ),
    Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
    Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
)


class DCPRRequestDataset(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(DCPRRequestDataset, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRRequestDataset"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRRequestNotificationTarget(
    core.StatefulObjectMixin, domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRRequestNotificationTarget, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRRequestNotificationTarget"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRGeospatialRequestNotificationTarget(
    core.StatefulObjectMixin, domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRGeospatialRequestNotificationTarget, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRGeospatialRequestNotificationTarget"]:
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
        datasets = (
            meta.Session.query(DCPRRequest)
            .join(
                DCPRRequestDataset,
                DCPRRequestDataset.dcpr_request_id == DCPRRequest.csi_reference_id,
            )
            .filter(DCPRRequestDataset.dcpr_request_id == str(self.csi_reference))
            .all()
        )

        return datasets

    def get_notification_targets(self) -> Optional[DCPRRequestNotificationTarget]:
        targets = (
            meta.Session.query(DCPRRequest)
            .join(
                DCPRRequestNotificationTarget,
                DCPRRequestNotificationTarget.dcpr_request_id
                == DCPRRequest.csi_reference_id,
            )
            .filter(
                DCPRRequestNotificationTarget.dcpr_request_id == str(self.csi_reference)
            )
            .all()
        )

        return targets


class DCPRGeospatialRequest(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(DCPRGeospatialRequest, self).__init__(**kw)
        self.csi_reference_id = kw.get("csi_reference_id", None)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRGeospatialRequest"]:
        """Finds a single request entity in the model."""
        query = meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    def get_notification_targets(
        self,
    ) -> Optional[DCPRGeospatialRequestNotificationTarget]:
        targets = (
            meta.Session.query(DCPRGeospatialRequest)
            .join(
                DCPRGeospatialRequestNotificationTarget,
                DCPRGeospatialRequestNotificationTarget.dcpr_request_id
                == DCPRGeospatialRequest.csi_reference_id,
            )
            .filter(
                DCPRGeospatialRequestNotificationTarget.dcpr_request_id
                == str(self.csi_reference)
            )
            .all()
        )

        return targets


meta.mapper(DCPRRequest, dcpr_request_table)
meta.mapper(DCPRRequestNotificationTarget, dcpr_request_notification_table)
meta.mapper(DCPRRequestDataset, dcpr_request_dataset_table)
meta.mapper(DCPRGeospatialRequest, dcpr_geospatial_request_table)
meta.mapper(DCPRRequestNotificationTarget, dcpr_geospatial_request_notification_table)
