"""Docker entrypoint for CKAN

This entrypoint script is inspired by CKAN's, but with some modifications, the
most obvious being that rather than a bash script, this is a Python module.

"""

import os
import sys
import time

import click

from ckan.cli import CKANConfigLoader
from ckan.config.environment import load_environment
from ckan.plugins import toolkit


@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--ckan-ini", envvar="CKAN_INI")
def launch_gunicorn(ckan_ini):
    click.secho(f"inside launch_gunicorn - ckan_ini is {ckan_ini}", fg="green")
    click.secho(f"Waiting for ckan environment to become available...", fg="green")
    available = _wait_for_ckan_env(ckan_ini)
    if available:
        click.secho(f"About to launch gunicorn...", fg="green")
        sys.stdout.flush()
        sys.stderr.flush()
        gunicorn_params = [
            "gunicorn",
            "ckanext.dalrrd_emc_dcpr.wsgi:application",
            f"--bind=0.0.0.0:5000",
            f"--error-logfile=-",
            f"--access-logfile=-",
        ]
        ckan_config = _get_ckan_config(ckan_ini)
        debug = toolkit.asbool(ckan_config.get("debug", False))
        if debug:
            gunicorn_params.extend([
                "--workers=1",
                "--reload",
                f"--log-level=debug",
            ])

        os.execvp("gunicorn", gunicorn_params)
    else:
        click.secho("ckan environment is not available, aborting...", fg="red")


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-c", "--ckan-ini", envvar="CKAN_INI")
@click.argument("ckan_args", nargs=-1, type=click.UNPROCESSED)
def launch_ckan_cli(ckan_ini, ckan_args):
    click.secho("inside launch_ckan_cli", fg="red")
    os.execvp(
        "ckan",
        ["ckan"] + list(ckan_args)
    )


def _wait_for_ckan_env(
        config_path: str, num_tries: int = 100, pause_for_seconds: int = 2) -> bool:
    """Try to load the ckan environment"""
    config = _get_ckan_config(config_path)
    total_tries = num_tries if num_tries > 0 else 1
    pause_for = pause_for_seconds if pause_for_seconds > 0 else 2
    for current_attempt in range(1, total_tries+1):
        try:
            load_environment(config)
        except Exception as exc:
            click.secho(
                f"({current_attempt}/{total_tries}) - ckan environment is not "
                f"available yet: {str(exc)}", fg="red"
            )
            click.secho(f"Retrying in {pause_for} seconds...")
            time.sleep(pause_for)
        else:
            result = True
            break
    else:
        result = False
    return result


def _get_ckan_config(config_path: str):
    config = CKANConfigLoader(config_path)
    return config.get_config()


if __name__ == "__main__":
    cli()
