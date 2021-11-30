"""CKAN CLI commands for the dalrrd-emc-dcpr extension"""

import logging

import click

logger = logging.getLogger(__name__)


@click.group(short_help="Commands related to the dalrrd-emc-dcpr extension.")
def dalrrd_emc_dcpr():
    """Commands related to the dalrrd-emc-dcpr extension."""


@dalrrd_emc_dcpr.command(short_help="Example command")
def test_ckan_command():
    click.secho("Hi world!", fg="green")
