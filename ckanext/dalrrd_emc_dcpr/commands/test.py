import click


@click.command("dalrrd-emc-dcpr-test")
def test_ckan_cmd():
    click.secho("hi there", fg="green")
