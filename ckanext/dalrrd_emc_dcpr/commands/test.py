import click


@click.command()
def test_ckan_cmd():
    click.secho("hi there", fg="green")
