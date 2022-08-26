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
    "metadata_point_of_contact-0-orgnizational_role",
    "reference_date",
    "iso_topic_category",
    "organization",
    "private",
    "dataset_language",
    "metadata_language",
    "dataset_character_set",
    "lineage-0-lineage_statement",
    "lineage-0-process_step_description",
    "distribution-0-distributor_contact",
    "maintainer",
    "spatial",
    "equivalent_scale",
    "spatial_representation_type",
    "spatial_reference_system",
    "metadata_stamp",
]
# choices fields
# status
# metadata_point_of_contact-0-orgnizational_role
# dataset_character_set
# dataset_character_set
# spatial_representation_type

# the equivalent_scale is teh spatial resolution field

DATASET_FULL_SET_OF_FIELDS = [
    "title",
    "name",
    "featured",
    "metadata_standard_name",
    "metadata_standard_version",
    "notes",
    "purpose",
    "acknowledgement",
    "status",
    "metadata_point_of_contact-0-individual_name",
    "metadata_point_of_contact-0-position_name",
    "metadata_point_of_contact-0-contact_point_address_city",
    "metadata_point_of_contact-0-contact_point_address_administrative_area",
    "metadata_point_of_contact-0-contact_point_postal_code",
    "metadata_point_of_contact-0- contact_point_electronic_mail_address",
    "metadata_point_of_contact-0-orgnizational_role",
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
    "lineage-0-level",
    "lineage-0-lineage_statement",
    "lineage-0-process_step_description",
    "lineage-0-process_step_datetime_from",
    "lineage-0-process_step_datetime_to",
    "lineage-0-processor_individual_name",
    "lineage-0-processing_owner_org",
    "lineage-0-processor_position_name",
    "lineage-0-processor_address_city",
    "lineage-0-processor_address_administrative_area",
    "lineage-0-processor_postal_code",
    "lineage-0-processor_electronic_mail_address",
    "distribution-0-distributor_contact",
    "distribution-0-distribution_order_process",
    "distribution-0-units_of_distribution",
    "distribution-0-distribution_online_source",
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
    "minimum_vertical_extent",
    "maximum_vertical_extent",
    "metadata_stamp",
]


class DCPRRequestRequiredFields(enum.Enum):
    SPATIAL_REFERENCE_SYSTEM = "EPSG:4326"
    DATASET_LANGUAGE = "en"
    DATASET_CHARACTER_SET = "ucs-2"
    METADATA_LANGUAGE = "en"
    ISO_TOPIC_CATEGORY = "location"
    LINEAGE = "Formed from a DCPR request"
    EQUIVALENT_SCALE = "10"
    SPATIAL_REPRESENTATION_TYPE = "001"
    NOTES = "Default notes"
