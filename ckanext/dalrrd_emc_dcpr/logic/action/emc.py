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


@toolkit.side_effect_free
def list_featured_datasets(
    context: typing.Dict,
    data_dict: typing.Optional[typing.Dict] = None,
) -> typing.List:
    toolkit.check_access("emc_authorize_list_featured_datasets", context, data_dict)
    data_ = data_dict.copy() if data_dict is not None else {}
    include_private = data_.get("include_private", False)
    limit = data_.get("limit", 10)
    offset = data_.get("offset", 0)
    model = context["model"]
    query = (
        sqlalchemy.select([model.package_table.c.name])
        .select_from(model.package_table.join(model.package_extra_table))
        .where(
            sqlalchemy.and_(
                model.package_extra_table.c.featured == "true",
                model.package_table.c.state == "active",
                model.package_table.c.private == include_private,
            )
        )
        .limit(limit)
        .offset(offset)
    )
    return [r for r in query.execute()]
