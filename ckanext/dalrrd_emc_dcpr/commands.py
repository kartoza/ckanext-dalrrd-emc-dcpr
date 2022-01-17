"""CKAN CLI commands for the dalrrd-emc-dcpr extension"""

import logging

import click

from ckan.plugins import toolkit

from .constants import SASDI_THEMES_VOCABULARY_NAME

logger = logging.getLogger(__name__)


@click.group(short_help="Commands related to the dalrrd-emc-dcpr extension.")
def dalrrd_emc_dcpr():
    """Commands related to the dalrrd-emc-dcpr extension."""


@dalrrd_emc_dcpr.command(short_help="Example command")
def test_ckan_command():
    click.secho("Hi world!", fg="green")


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
                fg="yellow",
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
                    fg="yellow",
                )
    click.secho("Done!", fg="green")


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
            fg="yellow",
        )
    click.secho(f"Done!", fg="green")


@bootstrap.command()
def create_organizations():
    """Create main SASDI organizations

    This command creates the main SASDI organizations: NSIF, CSI.

    It can safely be called multiple times - it will only ever create the
    organizations once, if they do not exist already.

    """
    organizations = [
        {
            "name": "NSIF",
            "description": "This is the NSIF organization",
            "image": None,
            "custom_fields": [],
            "members": [
                {
                    "id": None,
                    "role": "admin",
                }
            ],
        },
    ]
    for org_details in organizations:
        try:
            current_org = toolkit.get_action("organization_show")(
                context={},
                data_dict={
                    "id": org_details["name"],
                    "include_datasets": False,
                    "include_dataset_count": False,
                    "include_extras": True,
                    "include_users": True,
                    "include_groups": True,
                    "include_tags": True,
                },
            )
            click.echo(f"current_org: {current_org}")
        except toolkit.ObjectNotFound:
            click.echo(f"Could not find org {org_details['name']!r}")
