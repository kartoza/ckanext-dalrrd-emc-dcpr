import typing

from ckan.plugins import toolkit

from .. import constants
from . import _CkanBootstrapOrganization, _CkanExtBootstrapPage

_staff_org_title = toolkit.config.get(
    "ckan.dalrrd_emc_dcpr.portal_staff_organization_title", "SASDI EMC staff"
)
_staff_org_name = _staff_org_title.replace(" ", "-").lower()[:100]


SASDI_ORGANIZATIONS: typing.Final[typing.List[_CkanBootstrapOrganization]] = [
    _CkanBootstrapOrganization(
        name=constants.NSIF_ORG_NAME,
        title="NSIF",
        description=(
            "The National Spatial Information Framework (NSIF) is a directorate "
            "established in the Department of Rural Development and Land Reform, "
            "within the Branch: National Geomatics Management Services to "
            "facilitate the development and implementation of the South African "
            "Spatial Data Infrastructure (SASDI), established in terms of "
            "Section 3 of the Spatial Data Infrastructure Act (SDI Act No. 54, "
            "2003). The NSIF also serves as secretariat to the Committee for "
            "Spatial Information (CSI), established under Section 5 of the SDI "
            "Act. "
        ),
    ),
    _CkanBootstrapOrganization(
        name=constants.CSI_ORG_NAME,
        title="CSI",
        description=(
            "The Spatial Data Infrastructure Act (Act No. 54 of 2003) mandates "
            "the Committee for Spatial Information (CSI) to amongst others advise "
            "the Minister, the Director General and other Organs of State on "
            "matters regarding the capture, management, integration, distribution "
            "and utilisation of geo-spatial information. The CSI through its six "
            "subcommittees developed a Programme of Work to guide the work to be "
            "done by the CSI in achieving the objectives of SASDI."
        ),
    ),
    _CkanBootstrapOrganization(
        name=_staff_org_name,
        title=_staff_org_title,
        description=(
            f"The {_staff_org_title} organization is responsible for the maintenance of "
            f"the static contents for the EMC portal"
        ),
    ),
]

PORTAL_PAGES: typing.Final[typing.List[_CkanExtBootstrapPage]] = [
    _CkanExtBootstrapPage(
        name="help",
        content=(
            "This is the EMC help section. It contains resources to help you use the "
            "SASDI EMC effectively\n\n"
            "- [Frequently Asked Questions](frequently-asked-questions)"
        ),
        private=False,
        order="3",
    ),
    _CkanExtBootstrapPage(
        name="about",
        content=("Welcome to the SASDI Electronic Metadata Catalogue"),
        private=False,
        order="4",
    ),
    _CkanExtBootstrapPage(
        name="frequently-asked-questions",
        content=(
            "This is the default FAQ section\n\n"
            "1. What is this?\n\n"
            "    Its a metadata catalogue\n\n"
            "2. Can I link between pages?\n\n"
            "    It seems so: here is a link to the [help](help) page"
        ),
        private=False,
    ),
]
