import enum
import typing

SASDI_THEMES_VOCABULARY_NAME: typing.Final[str] = "sasdi_themes"

ISO_TOPIC_CATEGOY_VOCABULARY_NAME: typing.Final[str] = "iso_topic_categories"

ISO_TOPIC_CATEGORIES: typing.Final[typing.List[typing.Tuple[str, str]]] = [
    ("farming", "Farming"),
    ("biota", "Biota"),
    ("boundaries", "Boundaries"),
    ("climatologyMeteorologyAtmosphere", "Climatology, Meteorology, Atmosphere"),
    ("economy", "Economy"),
    ("elevation", "Elevation"),
    ("environment", "Environment"),
    ("geoscientificInformation", "Geoscientific Information"),
    ("health", "Health"),
    ("imageryBaseMapsEarthCover", "Imagery, Basemaps, Earth Cover"),
    ("intelligenceMilitary", "Intelligence, Millitary"),
    ("inlandWaters", "Inland Waters"),
    ("location", "Location"),
    ("oceans", "Oceans"),
    ("planningCadastre", "Planning, Cadastre"),
    ("society", "Society"),
    ("structure", "Structure"),
    ("transportation", "Transportation"),
    ("utilitiesCommuinication", "Utilities, Communication"),
]

NSIF_ORG_NAME = "nsif"
CSI_ORG_NAME = "csi"


class DatasetManagementActivityType(enum.Enum):
    REQUEST_MAINTENANCE = "requested dataset maintenance"
    REQUEST_PUBLICATION = "requested dataset publication"


class DcprManagementActivityType(enum.Enum):
    CREATE_DCPR_REQUEST = "created DCPR request"
    DELETE_DCPR_REQUEST = "deleted DCPR request"
    UPDATE_DCPR_REQUEST_BY_OWNER = "updated own DCPR request"
    UPDATE_DCPR_REQUEST_BY_NSIF = "updated DCPR request on behalf of NSIF"
    UPDATE_DCPR_REQUEST_BY_CSI = "updated DCPR request on behalf of CSI"
    SUBMIT_DCPR_REQUEST = "submitted DCPR request for review and moderation"
    BECOME_NSIF_REVIEWER_DCPR_REQUEST = "became DCPR request reviewer on behalf of NSIF"
    RESIGN_NSIF_REVIEWER_DCPR_REQUEST = (
        "resigned from DCPR request reviewer on behalf of NSIF"
    )
    BECOME_CSI_REVIEWER_DCPR_REQUEST = "became DCPR request reviewer on behalf of CSI"
    RESIGN_CSI_REVIEWER_DCPR_REQUEST = (
        "resigned from DCPR request reviewer on behalf of CSI"
    )
    ACCEPT_DCPR_REQUEST_NSIF = "accepted DCPR request on behalf of NSIF"
    REJECT_DCPR_REQUEST_NSIF = "rejected DCPR request on behalf of NSIF"
    REQUEST_CLARIFICATION_DCPR_REQUEST_NSIF = (
        "requested clarification on DCPR request on behalf of NSIF"
    )
    ACCEPT_DCPR_REQUEST_CSI = "accepted DCPR request on behalf of CSI"
    REJECT_DCPR_REQUEST_CSI = "rejected DCPR request on behalf of CSI"
    REQUEST_CLARIFICATION_DCPR_REQUEST_CSI = (
        "requested clarification on DCPR request on behalf of CSI"
    )


class DCPRRequestStatus(enum.Enum):
    UNDER_PREPARATION = "UNDER_PREPARATION"
    UNDER_MODIFICATION_REQUESTED_BY_NSIF = "UNDER_MODIFICATION_REQUESTED_BY_NSIF"
    UNDER_MODIFICATION_REQUESTED_BY_CSI = "UNDER_MODIFICATION_REQUESTED_BY_CSI"
    AWAITING_NSIF_REVIEW = "AWAITING_NSIF_REVIEW"
    UNDER_NSIF_REVIEW = "UNDER_NSIF_REVIEW"
    AWAITING_CSI_REVIEW = "AWAITING_CSI_REVIEW"
    UNDER_CSI_REVIEW = "UNDER_CSI_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class DcprRequestModerationAction(enum.Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CLARIFICATION = "REQUEST_CLARIFICATION"
    RESIGN = "RESIGN"


DATASET_MINIMAL_SET_OF_FIELDS = [
    "title",
    "name",
    "metadata_standard_name",
    "metadata_standard_version",
    "notes",
    "purpose",
    "status",
    "contact-0-organisational_role",
    "reference_date",
    "iso_topic_category",
    "owner_org",
    "private",
    "dataset_language",
    "metadata_language",
    "dataset_character_set",
    "metadata_character_set",
    "dataset_lineage-0-statement",
    "spatial",
    "equivalent_scale",
    "spatial_representation_type",
    "spatial_reference_system",
    "metadata_date_stamp",
]

DATASET_FULL_SET_OF_FIELDS = [
    "title",
    "name",
    "featured",
    "metadata_standard_name",
    "metadata_standard_version",
    "notes",
    "purpose",
    "doi",
    "acknowledgement",
    "status",
    "usage-0-specific_usage",
    "usage-0-datetime_from",
    "usage-0-datetime_to",
    "contact-0-individual_name",
    "contact-0-position_name",
    "contact-0-delivery_point",
    "contact-0-address_city",
    "contact-0-address_administrative_area",
    "contact-0-postal_code",
    "contact-0-electronic_mail_address",
    "contact-0-voice",
    "contact-0-facsimile",
    "contact-0-organisational_role",
    "owner_org",
    "private",
    "reference_date",
    "iso_topic_category",
    "sasdi_theme",
    "tag_string",
    "license_id",
    "url",
    "version",
    "dataset_language",
    "metadata_language",
    "dataset_character_set",
    "metadata_character_set",
    "dataset_lineage-0-level",
    "dataset_lineage-0-statement",
    "dataset_lineage-0-process_step_description",
    "dataset_lineage-0-process_step_rationale",
    "dataset_lineage-0-process_step_datetime_from",
    "dataset_lineage-0-process_step_datetime_to",
    "dataset_lineage-0-processor_individual_name",
    "dataset_lineage-0-processing_owner_org",
    "dataset_lineage-0-processor_position_name",
    "dataset_lineage-0-processor_address_city",
    "dataset_lineage-0-processor_address_administrative_area",
    "dataset_lineage-0-processor_postal_code",
    "dataset_lineage-0-processor_electronic_mail_address",
    "dataset_lineage-0-source_description",
    "dataset_lineage-0-source_scale_denominator",
    "dataset_lineage-0-source_reference_system",
    "distribution-0-transfer_size",
    "distribution-0-order_process",
    "distribution-0-units_of_distribution",
    "distribution-0-online_source",
    "distribution-0-offline_source",
    "maintainer",
    "maintainer_email",
    "maintenance_information-0-maintenance_and_update_frequency",
    "maintenance_information-0-maintenance_date_of_next_update",
    "maintenance_information-0-user_defined_maintenance_frequency",
    "maintenance_information-0-update_scope",
    "maintenance_information-0-update_scope_description",
    "maintenance_information-0-maintenance_notes",
    "spatial",
    "equivalent_scale",
    "spatial_representation_type",
    "spatial_reference_system",
    "temporal_reference_system",
    "reference_system_additional_info-0-temporal_extent_period_duration_from",
    "reference_system_additional_info-0-temporal_extent_period_duration_to",
    "reference_system_additional_info-0-description",
    "reference_system_additional_info-0-spatial_temporal_extent",
    "reference_system_additional_info-0-minimum_vertical_extent",
    "reference_system_additional_info-0-maximum_vertical_extent",
    "metadata_date_stamp",
]


class DCPRRequestRequiredFields(enum.Enum):
    DATASET_LANGUAGE = "en"
    DATASET_CHARACTER_SET = "ucs-2"
    METADATA_CHARACTER_SET = "ucs-2"
    DISTRIBUTOR_CONTACT = "contact"
    EQUIVALENT_SCALE = "10"
    ISO_TOPIC_CATEGORY = "location"
    LINEAGE_LEVEL = "001"
    LINEAGE_STATEMENT = "Formed from a DCPR request"
    LINEAGE_PROCESS_DESCRIPTION = "Formed from a DCPR request"
    METADATA_LANGUAGE = "en"
    METADATA_STANDARD_NAME = "standard name"
    METADATA_STANDARD_VERSION = "standard version"
    NOTES = "Default notes"
    PURPOSE = "Purpose"
    SPATIAL_REFERENCE_SYSTEM = "EPSG:4326"
    SPATIAL_REPRESENTATION_TYPE = "001"
    STATUS = "completed"
