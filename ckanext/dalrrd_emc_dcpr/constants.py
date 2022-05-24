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
