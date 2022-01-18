"""CKAN CLI commands for the dalrrd-emc-dcpr extension"""

import dataclasses
import logging
import typing
from functools import partial
from pathlib import Path

import click

from ckan.plugins import toolkit

from .constants import SASDI_THEMES_VOCABULARY_NAME

logger = logging.getLogger(__name__)

_DEFAULT_COLOR: typing.Final[typing.Optional[str]] = None
_SUCCESS_COLOR: typing.Final[str] = "green"
_ERROR_COLOR: typing.Final[str] = "red"
_INFO_COLOR: typing.Final[str] = "yellow"


@dataclasses.dataclass
class _CkanBootstrapOrganization:
    title: str
    description: str
    image_url: typing.Optional[Path] = None

    @property
    def name(self):
        return self.title.replace(" ", "-").lower()[:100]


_SASDI_ORGANIZATIONS: typing.Final[typing.List[_CkanBootstrapOrganization]] = [
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


@click.group(short_help="Commands related to the dalrrd-emc-dcpr extension.")
def dalrrd_emc_dcpr():
    """Commands related to the dalrrd-emc-dcpr extension."""


@dalrrd_emc_dcpr.group()
def bootstrap():
    """Commands for bootstrapping the dalrrd-emc-dcpr extension"""


@bootstrap.command()
def create_sasdi_themes():
    """Create SASDI themes

    This command adds a CKAN vocabulary for the SASDI themes and creates each theme
    as a CKAN tag.

    This command can safely be called multiple times - it will only ever create the
    vocabulary and themes once.

    """

    click.secho(
        f"Creating {SASDI_THEMES_VOCABULARY_NAME!r} CKAN tag vocabulary and adding "
        f"configured SASDI themes to it..."
    )

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    vocab_list = toolkit.get_action("vocabulary_list")(context)
    for voc in vocab_list:
        if voc["name"] == SASDI_THEMES_VOCABULARY_NAME:
            vocabulary = voc
            click.secho(
                (
                    f"Vocabulary {SASDI_THEMES_VOCABULARY_NAME!r} already exists, "
                    f"skipping creation..."
                ),
                fg=_INFO_COLOR,
            )
            break
    else:
        click.echo(f"Creating vocabulary {SASDI_THEMES_VOCABULARY_NAME!r}...")
        vocabulary = toolkit.get_action("vocabulary_create")(
            context, {"name": SASDI_THEMES_VOCABULARY_NAME}
        )

    for theme_name in toolkit.config.get(
        "ckan.dalrrd_emc_dcpr.sasdi_themes"
    ).splitlines():
        if theme_name != "":
            already_exists = theme_name in [tag["name"] for tag in vocabulary["tags"]]
            if not already_exists:
                click.echo(
                    f"Adding tag {theme_name!r} to "
                    f"vocabulary {SASDI_THEMES_VOCABULARY_NAME!r}..."
                )
                toolkit.get_action("tag_create")(
                    context, {"name": theme_name, "vocabulary_id": vocabulary["id"]}
                )
            else:
                click.secho(
                    (
                        f"Tag {theme_name!r} is already part of the "
                        f"{SASDI_THEMES_VOCABULARY_NAME!r} vocabulary, skipping..."
                    ),
                    fg=_INFO_COLOR,
                )
    click.secho("Done!", fg=_SUCCESS_COLOR)


@bootstrap.command()
def delete_sasdi_themes():
    """Delete SASDI themes

    This command adds a CKAN vocabulary for the SASDI themes and creates each theme
    as a CKAN tag.

    This command can safely be called multiple times - it will only ever delete the
    vocabulary and themes once, if they exist.

    """

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    vocabulary_list = toolkit.get_action("vocabulary_list")(context)
    if SASDI_THEMES_VOCABULARY_NAME in [voc["name"] for voc in vocabulary_list]:
        click.secho(
            f"Deleting {SASDI_THEMES_VOCABULARY_NAME!r} CKAN tag vocabulary and "
            f"respective tags... "
        )
        existing_tags = toolkit.get_action("tag_list")(
            context, {"vocabulary_id": SASDI_THEMES_VOCABULARY_NAME}
        )
        for tag_name in existing_tags:
            click.secho(f"Deleting tag {tag_name!r}...")
            toolkit.get_action("tag_delete")(
                context, {"id": tag_name, "vocabulary_id": SASDI_THEMES_VOCABULARY_NAME}
            )
        click.echo(f"Deleting vocabulary {SASDI_THEMES_VOCABULARY_NAME!r}...")
        toolkit.get_action("vocabulary_delete")(
            context, {"id": SASDI_THEMES_VOCABULARY_NAME}
        )
    else:
        click.secho(
            (
                f"Vocabulary {SASDI_THEMES_VOCABULARY_NAME!r} does not exist, "
                f"nothing to do"
            ),
            fg=_INFO_COLOR,
        )
    click.secho(f"Done!", fg=_SUCCESS_COLOR)


@bootstrap.command()
def create_sasdi_organizations():
    """Create main SASDI organizations

    This command creates the main SASDI organizations.

    This function may fail if the SASDI organizations already exist but are disabled,
    which can happen if they are deleted using the CKAN web frontend.

    This is a product of a CKAN limitation whereby it is not possible to retrieve a
    list of organizations regardless of their status - it will only return those that
    are active.

    """

    existing_organizations = toolkit.get_action("organization_list")(
        context={},
        data_dict={
            "organizations": [org.name for org in _SASDI_ORGANIZATIONS],
            "all_fields": False,
        },
    )
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    create_action: typing.Callable = partial(toolkit.get_action("organization_create"))
    for org_details in _SASDI_ORGANIZATIONS:
        if org_details.name not in existing_organizations:
            click.secho(f"Creating organization {org_details.name!r}...")
            try:
                create_action(
                    context={
                        "user": user["name"],
                        "return_id_only": True,
                    },
                    data_dict={
                        "name": org_details.name,
                        "title": org_details.title,
                        "description": org_details.description,
                        "image_url": org_details.image_url,
                    },
                )
            except toolkit.ValidationError as exc:
                click.secho(
                    f"Could not create organization {org_details.name!r}: {exc}",
                    fg=_ERROR_COLOR,
                )
    click.secho("Done!", fg=_SUCCESS_COLOR)


@bootstrap.command()
def delete_sasdi_organizations():
    """Delete the main SASDI organizations.

    This command will delete the SASDI organizations from the CKAN DB - CKAN refers to
    this as purging the organizations (the CKAN default behavior is to have the delete
    command simply disable the existing organizations, but keeping them in the DB).

    It can safely be called multiple times - it will only ever delete the
    organizations once.

    """

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    for org_details in _SASDI_ORGANIZATIONS:
        click.secho(f"Purging  organization {org_details.name!r}...")
        try:
            toolkit.get_action("organization_purge")(
                context={"user": user["name"]}, data_dict={"id": org_details.name}
            )
        except toolkit.ObjectNotFound:
            click.secho(
                f"Organization {org_details.name!r} does not exist, skipping...",
                fg=_INFO_COLOR,
            )
    click.secho(f"Done!", fg=_SUCCESS_COLOR)
