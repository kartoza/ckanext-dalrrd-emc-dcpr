"""Docker entrypoint for CKAN

This entrypoint script is inspired by CKAN's, but with some modifications, the
most obvious being that rather than a bash script, this is a Python module.

"""

import os
import sys

import click

from ckan.cli import load_config


@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--ckan-ini", envvar="CKAN_INI")
def launch_gunicorn(ckan_ini):
    click.secho(f"inside launch_gunicorn - ckan_ini is {ckan_ini}", fg="green")
    click.secho(f"About to launch gunicorn...", fg="green")
    sys.stdout.flush()
    sys.stderr.flush()
    ckan_config = load_config(ini_path=ckan_ini)
    port = ckan_config.get("ckan.devserver.port", "5000")
    # TODO: modify worker class according with the ckan config
    # TODO: modify log level according with the ckan config
    os.execvp(
        "gunicorn",
        [
            "gunicorn",
            "ckanext.dalrrd_emc_dcpr.wsgi:application",
            f"--bind=0.0.0.0:5000",
            f"--log-level=debug",
            f"--error-logfile=-",
            f"--access-logfile=-",
        ]
    )


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-c", "--ckan-ini", envvar="CKAN_INI")
@click.argument("ckan_args", nargs=-1, type=click.UNPROCESSED)
def launch_ckan_cli(ckan_ini, ckan_args):
    click.secho("inside launch_ckan_cli", fg="red")
    os.execvp(
        "ckan",
        ["ckan"] + list(ckan_args)
    )


if __name__ == "__main__":
    cli()
