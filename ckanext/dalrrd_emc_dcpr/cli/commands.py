"""CKAN CLI commands for the dalrrd-emc-dcpr extension"""

import json
import logging
import typing

import click

from ckan.plugins import toolkit
from ckan import model
from ckan.lib.navl import dictization_functions
from ckan.lib.email_notifications import get_and_send_notifications_for_all_users

from ..constants import (
    ISO_TOPIC_CATEGOY_VOCABULARY_NAME,
    ISO_TOPIC_CATEGORIES,
    SASDI_THEMES_VOCABULARY_NAME,
)

from ._bootstrap_data import SASDI_ORGANIZATIONS
from ._sample_datasets import SAMPLE_DATASETS
from ._sample_organizations import SAMPLE_ORGANIZATIONS
from ._sample_users import SAMPLE_USERS

logger = logging.getLogger(__name__)

_DEFAULT_COLOR: typing.Final[typing.Optional[str]] = None
_SUCCESS_COLOR: typing.Final[str] = "green"
_ERROR_COLOR: typing.Final[str] = "red"
_INFO_COLOR: typing.Final[str] = "yellow"


@click.group()
def dalrrd_emc_dcpr():
    """Commands related to the dalrrd-emc-dcpr extension."""


@dalrrd_emc_dcpr.command()
def send_email_notifications():
    """Send pending email notifications to users

    This command should be ran periodically.

    """

    # FIXME: This is failing with RuntimeError: Working outside of request context
    # seems like we need to call this function from the API instead
    setting_key = "ckan.activity_streams_email_notifications"
    send_notification_emails = toolkit.asbool(toolkit.config.get(setting_key))
    if toolkit.asbool(toolkit.config.get(setting_key)):
        get_and_send_notifications_for_all_users()
        click.secho("Done!", fg=_SUCCESS_COLOR)
    else:
        click.secho(
            f"{setting_key} is not enabled in config. Aborting", fg=_ERROR_COLOR
        )


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
                    f"vocabulary {ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r}..."
                )
                toolkit.get_action("tag_create")(
                    context, {"name": theme_name, "vocabulary_id": vocabulary["id"]}
                )
            else:
                click.secho(
                    (
                        f"Tag {theme_name!r} is already part of the "
                        f"{ISO_TOPIC_CATEGOY_VOCABULARY_NAME!r} vocabulary, skipping..."
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
            "organizations": [org.name for org in SASDI_ORGANIZATIONS],
            "all_fields": False,
        },
    )
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    for org_details in SASDI_ORGANIZATIONS:
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
    for org_details in SASDI_ORGANIZATIONS:
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
    for user_details in SAMPLE_USERS:
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
    for org_details, memberships, harvesters in SAMPLE_ORGANIZATIONS:
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
    for user_details in SAMPLE_USERS:
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
    for org_details, _, _ in SAMPLE_ORGANIZATIONS:
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


@load_sample_data.command()
def create_sample_datasets():
    """Create sample datasets"""

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    create_dataset_action = toolkit.get_action("package_create")
    get_dataset_action = toolkit.get_action("package_show")
    for dataset in SAMPLE_DATASETS:
        click.secho(f"Processing dataset {dataset.name!r}...")
        try:
            get_dataset_action(
                context={"user": user["name"]}, data_dict={"id": dataset.name}
            )
        except toolkit.ObjectNotFound:
            package_exists = False
        else:
            package_exists = True
            click.secho(f"dataset {dataset.name!r} already exists", fg=_INFO_COLOR)

        if not package_exists:
            click.secho(
                f"dataset {dataset.name!r} does not exist. Creating...", fg=_INFO_COLOR
            )
            data_dict = dataset.to_data_dict()
            click.secho(f"{data_dict=}", fg=_INFO_COLOR)
            try:
                create_dataset_action(
                    context={"user": user["name"]}, data_dict=data_dict
                )
            except dictization_functions.DataError as exc:
                click.secho(f"Could not create dataset: {exc=}", fg=_ERROR_COLOR)
    click.secho("Done!", fg=_SUCCESS_COLOR)


@delete_data.command()
def delete_sample_datasets():
    """Delete sample datasets"""
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    purge_dataset_action = toolkit.get_action("dataset_purge")
    get_dataset_action = toolkit.get_action("package_show")
    for dataset in SAMPLE_DATASETS:
        click.secho(f"Processing dataset {dataset.name!r}...")
        try:
            get_dataset_action(
                context={"user": user["name"]}, data_dict={"id": dataset.name}
            )
        except toolkit.ObjectNotFound:
            package_exists = False
            click.secho(
                f"dataset {dataset.name!r} does not exist. Skipping...", fg=_INFO_COLOR
            )
        else:
            package_exists = True
        if package_exists:
            click.secho(f"Purging dataset {dataset.name!r}...")
            purge_dataset_action(
                context={"user": user["name"]}, data_dict={"id": dataset.name}
            )
    click.secho("Done!", fg=_SUCCESS_COLOR)
