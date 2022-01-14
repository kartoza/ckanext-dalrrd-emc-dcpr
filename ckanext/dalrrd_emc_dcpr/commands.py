"""CKAN CLI commands for the dalrrd-emc-dcpr extension"""

import logging

import click

from ckan.plugins import toolkit

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

    vocabulary_name = "sasdi_themes"
    click.secho(
        f"Creating {vocabulary_name!r} CKAN tag vocabulary and adding configured SASDI "
        f"themes to it..."
    )

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    vocab_list = toolkit.get_action("vocabulary_list")(context)
    for voc in vocab_list:
        if voc["name"] == vocabulary_name:
            vocabulary = voc
            click.secho(
                f"Vocabulary {vocabulary_name!r} already exists, skipping creation...",
                fg="yellow",
            )
            break
    else:
        click.echo(f"Creating vocabulary {vocabulary_name!r}...")
        vocabulary = toolkit.get_action("vocabulary_create")(
            context, {"name": vocabulary_name}
        )

    for theme_name in toolkit.config.get(
        "ckan.dalrrd_emc_dcpr.sasdi_themes"
    ).splitlines():
        if theme_name != "":
            already_exists = theme_name in [tag["name"] for tag in vocabulary["tags"]]
            if not already_exists:
                click.echo(
                    f"Adding tag {theme_name!r} to vocabulary {vocabulary_name!r}..."
                )
                toolkit.get_action("tag_create")(
                    context, {"name": theme_name, "vocabulary_id": vocabulary["id"]}
                )
            else:
                click.secho(
                    f"Tag {theme_name!r} is already part of the {vocabulary_name!r} vocabulary, skipping...",
                    fg="yellow",
                )
    click.secho("Done!", fg="green")


@bootstrap.command(short_help="Example bootstrap command")
def delete_sasdi_themes():
    """Delete SASDI themes

    This command adds a CKAN vocabulary for the SASDI themes and creates each theme
    as a CKAN tag.

    This command can safely be called multiple times - it will only ever delete the
    vocabulary and themes once, if they exist.

    """

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    vocabulary_name = "sasdi_themes"
    vocabulary_list = toolkit.get_action("vocabulary_list")(context)
    if vocabulary_name in [voc["name"] for voc in vocabulary_list]:
        click.secho(
            f"Deleting {vocabulary_name!r} CKAN tag vocabulary and respective tags... "
        )
        existing_tags = toolkit.get_action("tag_list")(
            context, {"vocabulary_id": vocabulary_name}
        )
        for tag_name in existing_tags:
            click.secho(f"Deleting tag {tag_name!r}...")
            toolkit.get_action("tag_delete")(
                context, {"id": tag_name, "vocabulary_id": vocabulary_name}
            )
        click.echo(f"Deleting vocabulary {vocabulary_name!r}...")
        toolkit.get_action("vocabulary_delete")(context, {"id": vocabulary_name})
    else:
        click.secho(
            f"Vocabulary {vocabulary_name!r} does not exist, nothing to do", fg="yellow"
        )
    click.secho(f"Done!", fg="green")
