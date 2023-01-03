"""pytest configuration file"""

import pytest
import shlex
import sqlalchemy.exc
import subprocess

import ckan.model

pytest_plugins = (
    "ckan.tests.pytest_ckan.fixtures",
    "ckan.tests.pytest_ckan.ckan_setup",
)


@pytest.fixture
def emc_clean_db():
    """Reimplements cleaning the DB.

    This fixture exists because it does not seem to be easy to use a PostGIS
    DB to run CKAN tests. Additionally, there are some additional errors
    related to the harvesting extension. It seems ckan's
    `ckan.model.Repository.delete_all()` function can fail when trying to
    delete some harvesting-related tables when these do not exist yet.

    The implementation shown here is mostly an adaptation of
    `ckan.model.Repository.rebuild_db()` and `ckan.model.Repository.clean_db()`

    """

    ckan.model.Session.close_all()
    session = ckan.model.repo.session
    session.remove()
    tables = reversed(ckan.model.repo.metadata.sorted_tables)
    tables_to_keep = ("alembic_version",)
    for table in tables:
        if table.name in tables_to_keep:
            continue
        try:
            session.execute(f'DELETE FROM "{table.name}"')
        except sqlalchemy.exc.ProgrammingError:
            session.rollback()
        else:
            session.commit()
    session.flush()


@pytest.fixture
def emc_create_sasdi_themes(request):
    ckan_ini = request.config.getoption("--ckan-ini")
    subprocess.run(
        shlex.split(
            f"poetry run ckan --config {ckan_ini} dalrrd-emc-dcpr bootstrap create-iso-topic-categories"
        )
    )
