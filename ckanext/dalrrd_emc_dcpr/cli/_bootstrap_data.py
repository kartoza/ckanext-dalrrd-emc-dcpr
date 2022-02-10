import typing

from . import _CkanBootstrapOrganization


SASDI_ORGANIZATIONS: typing.Final[typing.List[_CkanBootstrapOrganization]] = [
    _CkanBootstrapOrganization(
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
]
