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


class ErrorReportStatus(enum.Enum):
    SUBMITTED = "SUBMITTED"
    MODIFICATION_REQUESTED = "MODIFICATION_REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ErrorReportModerationAction(enum.Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_MODIFICATION = "REQUEST_MODIFICATION"


DATASET_MINIMAL_SET_OF_FIELDS = [
    "title",
    "name",
    "notes",
    "responsible_party-0-individual_name",
    "responsible_party-0-role",
    "responsible_party-0-position_name",
    "metadata_reference_date_and_stamp-0-reference",
    "metadata_reference_date_and_stamp-0-reference_date_type",
    "topic_and_sasdi_theme-0-iso_topic_category",
    "owner_org",
    "private",
    "metadata_language_and_character_set-0-dataset_language",
    "metadata_language_and_character_set-0-metadata_language",
    "metadata_language_and_character_set-0-dataset_character_set",
    "metadata_language_and_character_set-0-metadata_character_set",
    "lineage_statement",
    "distribution_format-0-name",
    "distribution_format-0-version",
    "spatial",
    "spatial_parameters-0-equivalent_scale",
    "spatial_parameters-0-spatial_representation_type",
    "spatial_parameters-0-spatial_reference_system",
    "metadata_reference_date_and_stamp-0-stamp",
    "metadata_reference_date_and_stamp-0-stamp_date_type",
]

DATASET_FULL_SET_OF_FIELDS = [
    "title",
    "name",
    "featured",
    "doi",
    "metadata_standard-0-name",
    "metadata_standard-0-version",
    "notes",
    "responsible_party-0-individual_name",
    "responsible_party-0-position_name",
    "responsible_party-0-role",
    "responsible_party-0-electronic_mail_address",
    "responsible_party_contact_address-0-delivery_point",
    "responsible_party_contact_address-0-city",
    "responsible_party_contact_address-0-administrative_area",
    "responsible_party_contact_address-0-postal_code",
    "responsible_party_contact_info-0-voice",
    "responsible_party_contact_info-0-facsimile",
    "contact-0-individual_name",
    "contact-0-position_name",
    "contact-0-role",
    "contact-0-electronic_mail_address",
    "contact_address-0-delivery_point",
    "contact_address-0-city",
    "contact_address-0-administrative_area",
    "contact_address-0-postal_code",
    "contact_information-0-voice",
    "contact_information-0-facsimile",
    "owner_org",
    "private",
    "metadata_reference_date_and_stamp-0-reference",
    "metadata_reference_date_and_stamp-0-reference_date_type",
    "topic_and_sasdi_theme-0-iso_topic_category",
    "topic_and_sasdi_theme-0-sasdi_theme",
    "tag_string",
    "metadata_record_format-0-name",
    "metadata_record_format-0-version",
    "metadata_language_and_character_set-0-dataset_language",
    "metadata_language_and_character_set-0-metadata_language",
    "metadata_language_and_character_set-0-dataset_character_set",
    "metadata_language_and_character_set-0-metadata_character_set",
    "lineage_statement",
    "distribution_format-0-name",
    "distribution_format-0-version",
    "online_resource-0-name",
    "online_resource-0-linkeage",
    "online_resource-0-description",
    "online_resource-0-application_profile",
    "spatial",
    "spatial_parameters-0-equivalent_scale",
    "spatial_parameters-0-spatial_representation_type",
    "spatial_parameters-0-spatial_reference_system",
    "reference_system_additional_info",
    "metadata_reference_date_and_stamp-0-stamp",
    "metadata_reference_date_and_stamp-0-stamp_date_type",
]


XML_DATASET_NAMING_MAPPING = {
    "title": "title",
    "name": "name",
    "featured": "featured",
    "doi": "doi",
    "notes": "notes",
    "private": "private",
    "tagString": "tag_string",
    "MetadataStandardName": "metadata_standard-0-name",
    "MetadataStandardVersion": "metadata_standard-0-version",
    "OwnerOrg": "owner_org",
    "ResponsiblePartyIndividualName": "responsible_party-0-individual_name",
    "ResponsiblePartyRole": "responsible_party-0-role",
    "ResponsiblePartyPositionName": "responsible_party-0-position_name",
    "ResponsiblePartyElectronicMailAddress": "responsible_party-0-electronic_mail_address",
    "ResponsiblePartyContactAddressDeliveryPoint": "responsible_party_contact_address-0-delivery_point",
    "ResponsiblePartyContactAddressCity": "responsible_party_contact_address-0-city",
    "ResponsiblePartyContactAddressAdministrativeArea": "responsible_party_contact_address-0-administrative_area",
    "ResponsiblePartyContactAddressPostalCode": "responsible_party_contact_address-0-postal_code",
    "ResponsiblePartyContactInfoVoice": "responsible_party_contact_info-0-voice",
    "ResponsiblePartyContactInfoFacsimile": "responsible_party_contact_info-0-facsimile",
    "ReferenceDate": "metadata_reference_date_and_stamp-0-reference",
    "ReferenceDateType": "metadata_reference_date_and_stamp-0-reference_date_type",
    "IsoTopicCategory": "topic_and_sasdi_theme-0-iso_topic_category",
    "LineageStatement": "lineage_statement",
    "DatasetLanguage": "metadata_language_and_character_set-0-dataset_language",
    "MetadataLanguage": "metadata_language_and_character_set-0-metadata_language",
    "DatasetCharacterset": "metadata_language_and_character_set-0-dataset_character_set",
    "MetadataCharacterset": "metadata_language_and_character_set-0-metadata_character_set",
    "DistributionFormatName": "distribution_format-0-name",
    "DistributionFormatVersion": "distribution_format-0-version",
    "spatial": "spatial",
    "EquivalentScale": "spatial_parameters-0-equivalent_scale",
    "SpatialRepresentationType": "spatial_parameters-0-spatial_representation_type",
    "SpatialReferenceSystem": "spatial_parameters-0-spatial_reference_system",
    "StampDate": "metadata_reference_date_and_stamp-0-stamp",
    "StampDateType": "metadata_reference_date_and_stamp-0-stamp_date_type",
    "ContactIndividualName": "contact-0-individual_name",
    "ContactPositionName": "contact-0-position_name",
    "ContactRole": "contact-0-role",
    "ContactElectronicMailAddress": "contact-0-electronic_mail_address",
    "ContactAddressDeliveryPoint": "contact_address-0-delivery_point",
    "ContactAddressCity": "contact_address-0-city",
    "ContactAddressAdministrativeArea": "contact_address-0-administrative_area",
    "ContactAddressPostalCode": "contact_address-0-postal_code",
    "ContactInformationVoice": "contact_information-0-voice",
    "ContactInformationFacsimile": "contact_information-0-facsimile",
}


class DCPRRequestRequiredFields(enum.Enum):
    DATASET_LANGUAGE = "en"
    DATASET_CHARACTER_SET = "ucs-2"
    METADATA_CHARACTER_SET = "ucs-2"
    DISTRIBUTION_FORMAT_NAME = "format"
    DISTRIBUTION_FORMAT_VERSION = "version"
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
    REFERENCE_DATE_TYPE = "Creation"
    STAMP_DATE_TYPE = "Creation"
    RESPONSIBLE_PARTY_INDIVIDUAL_NAME = "individual_name"
    RESPONSIBLE_PARTY_POSITION_NAME = "dataset custodian"
    RESPONSIBLE_PARTY_ROLE = "owner"
