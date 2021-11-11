import os
import click
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
import ckan.model as model
import ckan.plugins.toolkit as toolkit


@click.command(
    short_help=u"Adds datastore user defined in"
               u" the ckan configurations to the datastore database.")
def create_datastore_user():
    """ Creates user in a datastore database with read only access.
        User credential are from the already defined ckan.datastore.read_url
        setting in CKAN configurations.
    """
    db = create_engine(toolkit.config['ckan.datastore.write_url'])
    db_read_url_parts = model.parse_db_config('ckan.datastore.read_url')

    user_name = db_read_url_parts["db_user"]
    user_password = db_read_url_parts["db_pass"]

    try:
        sql = f"CREATE USER \"{user_name}\" WITH PASSWORD '%s'" % user_password
        db.execute(sql)

    except ProgrammingError as error:
        click.echo(f"Error occured while creating user {error}")
