import logging
import os
import pkg_resources
import typing

import ckan.plugins.toolkit as toolkit
import sqlalchemy
from ckan.logic.schema import default_create_activity_schema

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


def request_dataset_maintenance(context: typing.Dict, data_dict: typing.Dict):
    toolkit.check_access("emc_request_dataset_maintenance", context, data_dict)
    activity_schema = default_create_activity_schema()

    # this is a hacky way to relax the activity type schema validation
    to_remove = None
    for index, validator in enumerate(activity_schema["activity_type"]):
        if validator.__name__ == "activity_type_exists":
            to_remove = validator
            break
    if to_remove:
        activity_schema["activity_type"].remove(to_remove)
    to_remove = None
    for index, validator in enumerate(activity_schema["object_id"]):
        if validator.__name__ == "object_id_validator":
            to_remove = validator
            break
    if to_remove:
        activity_schema["object_id"].remove(to_remove)
    activity_schema["object_id"].append(toolkit.get_validator("package_id_exists"))

    logger.debug(f"{activity_schema=}")
    toolkit.get_action("activity_create")(
        context={
            "ignore_auth": True,
            "schema": activity_schema,
        },
        data_dict={
            "user_id": toolkit.g.userobj.id,
            "object_id": data_dict["pkg_id"],
            "activity_type": "requested modification",
            "data": None,
        },
    )
