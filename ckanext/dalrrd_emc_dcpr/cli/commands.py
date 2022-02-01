"""CKAN CLI commands for the dalrrd-emc-dcpr extension"""

import dataclasses
import json
import logging
import typing
from pathlib import Path

import click

from ckan.plugins import toolkit
from ckan import model
from ckanext.harvest import model as harvest_model

from ..constants import (
    ISO_TOPIC_CATEGOY_VOCABULARY_NAME,
    ISO_TOPIC_CATEGORIES,
    SASDI_THEMES_VOCABULARY_NAME,
)

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


@dataclasses.dataclass
class _CkanBootstrapUser:
    name: str
    email: str
    password: str


@dataclasses.dataclass
class _CkanBootstrapHarvester:
    name: str
    url: str
    source_type: str
    update_frequency: str
    configuration: typing.Dict


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

_SAMPLE_USER_PASSWORD: typing.Final[str] = "12345678"

_SAMPLE_USERS: typing.Final[typing.List[_CkanBootstrapUser]] = [
    _CkanBootstrapUser("tester1", "tester1@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester2", "tester2@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester3", "tester3@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester4", "tester4@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester5", "tester5@fake.mail", _SAMPLE_USER_PASSWORD),
    _CkanBootstrapUser("tester6", "tester6@fake.mail", _SAMPLE_USER_PASSWORD),
]

_SAMPLE_ORG_DESCRIPTION: typing.Final[str] = (
    "This is a sample organization. It is meant for aiding the development and "
    "testing purposes"
)

_SAMPLE_ORGANIZATIONS: typing.Final[
    typing.List[
        typing.Tuple[
            _CkanBootstrapOrganization,
            typing.List[typing.Tuple[str, str]],
            typing.List[_CkanBootstrapHarvester],
        ]
    ]
] = [
    (
        _CkanBootstrapOrganization("Sample org 1", _SAMPLE_ORG_DESCRIPTION),
        [
            ("tester1", "member"),
            ("tester2", "editor"),
            ("tester3", "publisher"),
        ],
        [
            _CkanBootstrapHarvester(
                name="local-pycsw",
                url="http://csw-harvest-target:8000",
                source_type="csw",
                update_frequency="MANUAL",
                configuration={"default_tags": ["csw", "harvest"]},
            )
        ],
    ),
    (
        _CkanBootstrapOrganization("Sample org 2", _SAMPLE_ORG_DESCRIPTION),
        [
            ("tester4", "member"),
            ("tester5", "editor"),
            ("tester6", "publisher"),
        ],
        [],
    ),
]


@click.group()
def dalrrd_emc_dcpr():
    """Commands related to the dalrrd-emc-dcpr extension."""


@dalrrd_emc_dcpr.group()
def bootstrap():
    """Bootstrap the dalrrd-emc-dcpr extension"""


@dalrrd_emc_dcpr.group()
def delete_data():
    """Delete dalrrd-emc-dcpr bootstrapped and sample data"""


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


@delete_data.command()
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
def create_iso_topic_categories():
    """Create ISO Topic Categories.

    This command adds a CKAN vocabulary for the ISO Topic Categories and creates each
    topic category as a CKAN tag.

    This command can safely be called multiple times - it will only ever create the
    vocabulary and themes once.

    """

    click.secho(
        f"Creating ISO Topic Categories CKAN tag vocabulary and adding "
        f"the relevant categories..."
    )

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    vocab_list = toolkit.get_action("vocabulary_list")(context)
    for voc in vocab_list:
        if voc["name"] == ISO_TOPIC_CATEGOY_VOCABULARY_NAME:
            vocabulary = voc
            click.secho(
                (
                    f"Vocabulary {ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r} already exists, "
                    f"skipping creation..."
                ),
                fg=_INFO_COLOR,
            )
            break
    else:
        click.echo(f"Creating vocabulary {ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r}...")
        vocabulary = toolkit.get_action("vocabulary_create")(
            context, {"name": ISO_TOPIC_CATEGOY_VOCABULARY_NAME}
        )

    for theme_name, _ in ISO_TOPIC_CATEGORIES:
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


@delete_data.command()
def delete_iso_topic_categories():
    """Delete ISO Topic Categories.

    This command can safely be called multiple times - it will only ever delete the
    vocabulary and themes once, if they exist.

    """

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    vocabulary_list = toolkit.get_action("vocabulary_list")(context)
    if ISO_TOPIC_CATEGOY_VOCABULARY_NAME in [voc["name"] for voc in vocabulary_list]:
        click.secho(
            f"Deleting {ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r} CKAN tag vocabulary and "
            f"respective tags... "
        )
        existing_tags = toolkit.get_action("tag_list")(
            context, {"vocabulary_id": ISO_TOPIC_CATEGOY_VOCABULARY_NAME}
        )
        for tag_name in existing_tags:
            click.secho(f"Deleting tag {tag_name!r}...")
            toolkit.get_action("tag_delete")(
                context,
                {"id": tag_name, "vocabulary_id": ISO_TOPIC_CATEGOY_VOCABULARY_NAME},
            )
        click.echo(f"Deleting vocabulary {ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r}...")
        toolkit.get_action("vocabulary_delete")(
            context, {"id": ISO_TOPIC_CATEGOY_VOCABULARY_NAME}
        )
    else:
        click.secho(
            (
                f"Vocabulary {ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r} does not exist, "
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
    for org_details in _SASDI_ORGANIZATIONS:
        if org_details.name not in existing_organizations:
            click.secho(f"Creating organization {org_details.name!r}...")
            try:
                toolkit.get_action("organization_create")(
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


@delete_data.command()
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


@dalrrd_emc_dcpr.group()
def load_sample_data():
    """Load sample data into non-production deployments"""


@load_sample_data.command()
def create_sample_users():
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    create_user_action = toolkit.get_action("user_create")
    click.secho(f"Creating sample users ...")
    for user_details in _SAMPLE_USERS:
        click.secho(f"Creating {user_details.name!r}...")
        try:
            create_user_action(
                context={
                    "user": user["name"],
                },
                data_dict={
                    "name": user_details.name,
                    "email": user_details.email,
                    "password": user_details.password,
                },
            )
        except toolkit.ValidationError as exc:
            click.secho(
                f"Could not create user {user_details.name!r}: {exc}", fg=_INFO_COLOR
            )
            click.secho(
                f"Attempting to re-enable possibly deleted user...", fg=_INFO_COLOR
            )
            sample_user = model.User.get(user_details.name)
            if sample_user is None:
                click.secho(
                    f"Could not find sample_user {user_details.name!r}", fg=_ERROR_COLOR
                )
                continue
            else:
                sample_user.undelete()
                model.repo.commit()


@load_sample_data.command()
def create_sample_organizations():
    """Create sample organizations and members"""
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    create_org_action = toolkit.get_action("organization_create")
    create_org_member_action = toolkit.get_action("organization_member_create")
    create_harvester_action = toolkit.get_action("harvest_source_create")
    click.secho(f"Creating sample organizations ...")
    for org_details, memberships, harvesters in _SAMPLE_ORGANIZATIONS:
        click.secho(f"Creating {org_details.name!r}...")
        try:
            create_org_action(
                context={
                    "user": user["name"],
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
        for user_name, role in memberships:
            click.secho(f"Creating membership {user_name!r} ({role!r})...")
            create_org_member_action(
                context={
                    "user": user["name"],
                },
                data_dict={
                    "id": org_details.name,
                    "username": user_name,
                    "role": role if role != "publisher" else "admin",
                },
            )
        for harvester_details in harvesters:
            click.secho(f"Creating harvest source {harvester_details.name!r}...")
            try:
                create_harvester_action(
                    context={"user": user["name"]},
                    data_dict={
                        "name": harvester_details.name,
                        "url": harvester_details.url,
                        "source_type": harvester_details.source_type,
                        "frequency": harvester_details.update_frequency,
                        "config": json.dumps(harvester_details.configuration),
                        "owner_org": org_details.name,
                    },
                )
            except toolkit.ValidationError as exc:
                click.secho(
                    (
                        f"Could not create harvest source "
                        f"{harvester_details.name!r}: {exc}"
                    ),
                    fg=_INFO_COLOR,
                )
                click.secho(
                    f"Attempting to re-enable possibly deleted harvester source...",
                    fg=_INFO_COLOR,
                )
                sample_harvester = model.Package.get(harvester_details.name)
                if sample_harvester is None:
                    click.secho(
                        f"Could not find harvester source {harvester_details.name!r}",
                        fg=_ERROR_COLOR,
                    )
                    continue
                else:
                    sample_harvester.state = model.State.ACTIVE
                    model.repo.commit()
    click.secho("Done!", fg=_SUCCESS_COLOR)


@delete_data.command()
def delete_sample_users():
    """Delete sample users."""
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    delete_user_action = toolkit.get_action("user_delete")
    click.secho(f"Deleting sample users ...")
    for user_details in _SAMPLE_USERS:
        click.secho(f"Deleting {user_details.name!r}...")
        delete_user_action(
            context={"user": user["name"]},
            data_dict={"id": user_details.name},
        )
    click.secho("Done!", fg=_SUCCESS_COLOR)


@delete_data.command()
def delete_sample_organizations():
    """Delete sample organizations."""
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    org_show_action = toolkit.get_action("organization_show")
    purge_org_action = toolkit.get_action("organization_purge")
    package_search_action = toolkit.get_action("package_search")
    dataset_purge_action = toolkit.get_action("dataset_purge")
    harvest_source_list_action = toolkit.get_action("harvest_source_list")
    harvest_source_delete_action = toolkit.get_action("harvest_source_delete")
    click.secho(f"Purging sample organizations ...")
    for org_details, _, _ in _SAMPLE_ORGANIZATIONS:
        try:
            org = org_show_action(
                context={"user": user["name"]}, data_dict={"id": org_details.name}
            )
            click.secho(f"{org = }", fg=_INFO_COLOR)
        except toolkit.ObjectNotFound:
            click.secho(
                f"Organization {org_details.name} does not exist, skipping...",
                fg=_INFO_COLOR,
            )
        else:
            packages = package_search_action(
                context={"user": user["name"]},
                data_dict={"fq": f"owner_org:{org['id']}"},
            )
            click.secho(f"{packages = }", fg=_INFO_COLOR)
            for package in packages["results"]:
                click.secho(f"Purging package {package['id']}...")
                dataset_purge_action(
                    context={"user": user["name"]}, data_dict={"id": package["id"]}
                )
            harvest_sources = harvest_source_list_action(
                context={"user": user["name"]}, data_dict={"organization_id": org["id"]}
            )
            click.secho(f"{ harvest_sources = }", fg=_INFO_COLOR)
            for harvest_source in harvest_sources:
                click.secho(f"Deleting harvest_source {harvest_source['title']}...")
                harvest_source_delete_action(
                    context={"user": user["name"], "clear_source": True},
                    data_dict={"id": harvest_source["id"]},
                )
            click.secho(f"Purging {org_details.name!r}...")
            purge_org_action(
                context={"user": user["name"]},
                data_dict={"id": org["id"]},
            )
    click.secho("Done!", fg=_SUCCESS_COLOR)
