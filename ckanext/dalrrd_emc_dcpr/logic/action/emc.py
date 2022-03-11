import logging
import os
import pkg_resources
import typing

import ckan.plugins.toolkit as toolkit
import sqlalchemy

logger = logging.getLogger(__name__)


@toolkit.side_effect_free
def show_version(
    context: typing.Optional[typing.Dict] = None,
    data_dict: typing.Optional[typing.Dict] = None,
) -> typing.Dict:
    """return the current version of this project"""
    return {
        "version": pkg_resources.require("ckanext-dalrrd-emc-dcpr")[0].version,
        "git_sha": os.getenv("GIT_COMMIT"),
    }
