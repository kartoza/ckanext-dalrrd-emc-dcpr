import datetime
import enum
from typing import Optional

from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey

from ckan import model

dcpr_request_table = Table(
    "dcpr_request",
    model.meta.metadata,
    Column(
        "csi_reference_id",
        types.UnicodeText,
        primary_key=True,
        default=model.types.make_uuid,
    ),
    Column(
        "owner_user",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    ),
    Column(
        "organization_id",
        types.UnicodeText,
        ForeignKey("group.id"),
        nullable=False,
    ),
    Column(
        "csi_moderator",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=True,
    ),
    Column(
        "nsif_reviewer",
        types.UnicodeText,
        ForeignKey("user.id"),
        nullable=True,
    ),
    Column("status", types.UnicodeText),
    Column("proposed_project_name", types.UnicodeText),
    Column("additional_project_context", types.UnicodeText),
    Column("capture_start_date", types.DateTime),
    Column("capture_end_date", types.DateTime),
    Column("cost", types.UnicodeText),
    Column("spatial_extent", types.UnicodeText),
    Column("spatial_resolution", types.UnicodeText),
    Column("data_capture_urgency", types.UnicodeText),
    Column("additional_information", types.UnicodeText),
    Column("additional_documents", types.UnicodeText),
    Column("request_date", types.DateTime, default=datetime.datetime.utcnow),
    Column("submission_date", types.DateTime),
    Column("nsif_review_date", types.DateTime),
    Column("nsif_recommendation", types.UnicodeText),
    Column("nsif_review_notes", types.UnicodeText),
    Column("nsif_review_additional_documents", types.UnicodeText),
    Column("csi_moderation_notes", types.UnicodeText),
    Column("csi_moderation_additional_documents", types.UnicodeText),
    Column("csi_moderation_date", types.DateTime),
    Column("organisation_level", types.UnicodeText),
    Column("organisation_address", types.UnicodeText),
    Column("contact_person_name", types.UnicodeText),
    Column("contact_person_designation", types.UnicodeText),
    Column("contact_person_email_address", types.UnicodeText),
    Column("dcpr_contact_person_phone", types.UnicodeText),
    Column("dcpr_contact_person_fax_number", types.UnicodeText),
)

dcpr_request_dataset_table = Table(
    "dcpr_request_dataset",
    model.meta.metadata,
    Column(
        "dataset_id", types.UnicodeText, primary_key=True, default=model.types.make_uuid
    ),
    Column("dcpr_request_id", ForeignKey("dcpr_request.csi_reference_id")),
    Column("dataset_custodian", types.Boolean, default=False),
    Column("data_type", types.UnicodeText),
    Column("proposed_dataset_title", types.UnicodeText, nullable=False),
    Column("proposed_abstract", types.UnicodeText),
    Column("dataset_purpose", types.UnicodeText, nullable=False),
    Column("lineage_statement", types.UnicodeText),
    Column("associated_attributes", types.UnicodeText),
    Column("feature_description", types.UnicodeText),
    Column("data_usage_restrictions", types.UnicodeText),
    Column("capture_method", types.UnicodeText),
    Column("capture_method_detail", types.UnicodeText),
    Column("topic_category", types.UnicodeText),
    Column("dataset_characterset", types.UnicodeText),
    Column("metadata_characterset", types.UnicodeText),
)

dcpr_request_notification_table = Table(
    "dcpr_request_notification",
    model.meta.metadata,
    Column(
        "target_id", types.UnicodeText, primary_key=True, default=model.types.make_uuid
    ),
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
    model.meta.metadata,
    Column(
        "csi_reference_id",
        types.UnicodeText,
        primary_key=True,
        default=model.types.make_uuid,
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
    model.meta.metadata,
    Column(
        "target_id", types.UnicodeText, primary_key=True, default=model.types.make_uuid
    ),
    Column(
        "dcpr_geospatial_request_id",
        types.UnicodeText,
        ForeignKey("dcpr_geospatial_request.csi_reference_id"),
    ),
    Column("user_id", types.UnicodeText, ForeignKey("user.id"), nullable=True),
    Column("group_id", types.UnicodeText, ForeignKey("group.id"), nullable=True),
)


class DCPRRequestOrganizationLevel(enum.Enum):
    NATIONAL = "National"
    PROVINCIAL = "Provincial"
    MUNICIPAL = "Municipal"
    TRIBAL = "Tribal"
    AUTHORITY = "Authority"


class DCPRRequestUrgency(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DCPRCaptureMethod(enum.Enum):

    AERIAL_PHOTOGRAPHY = "Aerial Photography"
    DIGITIZING = "Digitizing"
    GPS = "GPS coordinate capture"
    REMOTE_SENSING = "Remote sensing"
    SCANNING = "Scanning & vectorising"
    SURVEY = "Survey (cadastral)"
    SURVEY_QUESTIONNAIRE = "Survey (questionnaire)"


class DCPRTOPICCATEGORY(enum.Enum):

    Farming = "farming"
    Biota = "biota"
    Boundaries = "boundaries"
    Climatology_Meteorology_Atmosphere = "climatologyMeteorologyAtmosphere"
    Economy = "economy"
    Elevation = "elevation"
    Environment = "environment"
    Geoscientific_Information = "geoscientificInformation"
    Health = "health"
    Imagery_Basemaps_Earth_Cover = "imageryBaseMapsEarthCover"
    Intelligence_Millitary = "intelligenceMilitary"
    Inland_Waters = "inlandWaters"
    Location = "location"
    Oceans = "oceans"
    Planning_Cadastre = "planningCadastre"
    Society = "society"
    Structure = "structure"
    Transportation = "transportation"
    Utilities_Communication = "utilitiesCommuinication"


class DCPRCHARACTERSET(enum.Enum):

    UCS_2 = "ucs-2"
    UCS_4 = "ucs-4"
    UTF_7 = "utf-7"
    UTF_8 = "utf-8"
    UTF_16 = "utf-16"
    ISO8859_1 = "8859part1"
    ISO8859_2 = "8859part2"
    ISO8859_3 = "8859part3"
    ISO8859_4 = "8859part4"
    ISO8859_5 = "8859part5"
    ISO8859_6 = "8859part6"
    ISO8859_7 = "8859part7"
    ISO8859_8 = "8859part8"
    ISO8859_9 = "8859part9"
    ISO8859_10 = "8859part10"
    ISO8859_11 = "8859part11"
    ISO8859_13 = "8859part13"
    ISO8859_14 = "8859part14"
    ISO8859_15 = "8859part15"
    ISO8859_16 = "8859part16"
    jis = "jis"
    shiftJIS = "shiftJIS"
    eucJP = "eucJP"
    ASCII = "usAscii"
    ebcdic = "ebcdic"
    eucKR = "eucKR"
    big5 = "big5"
    GB2312 = "GB2312"


class DCPRRequestDataset(
    model.core.StatefulObjectMixin, model.domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRRequestDataset, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRRequestDataset"]:
        """Finds a single request entity in the model."""
        query = model.meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRRequestNotificationTarget(
    model.core.StatefulObjectMixin, model.domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRRequestNotificationTarget, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRRequestNotificationTarget"]:
        """Finds a single request entity in the model."""
        query = model.meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRGeospatialRequestNotificationTarget(
    model.core.StatefulObjectMixin, model.domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRGeospatialRequestNotificationTarget, self).__init__(**kw)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRGeospatialRequestNotificationTarget"]:
        """Finds a single request entity in the model."""
        query = model.meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()


class DCPRRequest(model.core.StatefulObjectMixin, model.domain_object.DomainObject):
    def __init__(self, **kw):
        super(DCPRRequest, self).__init__(**kw)
        self.csi_reference_id = kw.get("csi_reference_id", None)

    @classmethod
    def get(cls, csi_reference_id) -> Optional["DCPRRequest"]:
        """Finds a single request entity in the model."""
        query = model.meta.Session.query(cls)
        return query.get(csi_reference_id)

    #
    # def get_dataset_elements(self) -> Optional[DCPRRequestDataset]:
    #     datasets = (
    #         model.meta.Session.query(DCPRRequest)
    #         .join(
    #             DCPRRequestDataset,
    #             DCPRRequestDataset.dcpr_request_id == DCPRRequest.csi_reference_id,
    #         )
    #         .filter(DCPRRequestDataset.dcpr_request_id == str(self.csi_reference))
    #         .all()
    #     )
    #
    #     return datasets

    def get_notification_targets(self) -> Optional[DCPRRequestNotificationTarget]:
        targets = (
            model.meta.Session.query(DCPRRequest)
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


class DCPRGeospatialRequest(
    model.core.StatefulObjectMixin, model.domain_object.DomainObject
):
    def __init__(self, **kw):
        super(DCPRGeospatialRequest, self).__init__(**kw)
        self.csi_reference_id = kw.get("csi_reference_id", None)

    @classmethod
    def get(cls, **kw) -> Optional["DCPRGeospatialRequest"]:
        """Finds a single request entity in the model."""
        query = model.meta.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    def get_notification_targets(
        self,
    ) -> Optional[DCPRGeospatialRequestNotificationTarget]:
        targets = (
            model.meta.Session.query(DCPRGeospatialRequest)
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


model.meta.mapper(
    DCPRRequest,
    dcpr_request_table,
    properties={
        "owner": orm.relationship(
            model.User,
            backref="dcpr_requests",
            foreign_keys=dcpr_request_table.c.owner_user,
        ),
        "organization": orm.relationship(
            model.Group,
            backref="dcpr_requests",
        ),
        "user_nsif_reviewer": orm.relationship(
            model.User,
            backref="nsif_reviewer_dcpr_requests",
            foreign_keys=dcpr_request_table.c.nsif_reviewer,
        ),
        "user_csi_reviewer": orm.relationship(
            model.User,
            backref="csi_reviewer_dcpr_requests",
            foreign_keys=dcpr_request_table.c.csi_moderator,
        ),
    },
)
model.meta.mapper(DCPRRequestNotificationTarget, dcpr_request_notification_table)
model.meta.mapper(
    DCPRRequestDataset,
    dcpr_request_dataset_table,
    properties={
        "dcpr_request": orm.relationship(
            DCPRRequest,
            backref=orm.backref("datasets", cascade="all, delete, delete-orphan"),
        )
    },
)
model.meta.mapper(DCPRGeospatialRequest, dcpr_geospatial_request_table)
model.meta.mapper(
    DCPRGeospatialRequestNotificationTarget, dcpr_geospatial_request_notification_table
)
