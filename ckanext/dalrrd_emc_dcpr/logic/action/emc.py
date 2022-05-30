import logging
import os
import pkg_resources
import typing

import ckan.plugins.toolkit as toolkit
import sqlalchemy

from ... import jobs
from ...constants import DatasetManagementActivityType

from . import create_dataset_management_activity

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
    """Request that a dataset be put on maintenance mode (AKA make it private)

    This action performs the following:

    - Create a new activity, so that it shows up on the user dashboard
    - Enqueue background job which will email the dataset's owner_org admins
    - Ensure user is registered to receive email notifications
    - Ensure user is following the dataset

    """

    toolkit.check_access("emc_request_dataset_maintenance", context, data_dict)
    activity = create_dataset_management_activity(
        data_dict["pkg_id"], DatasetManagementActivityType.REQUEST_MAINTENANCE
    )
    _ensure_user_is_notifiable(context["user"], data_dict["pkg_id"])
    toolkit.enqueue_job(
        jobs.notify_org_admins_of_dataset_management_request,
        args=[activity["id"]],
    )


def request_dataset_publication(context: typing.Dict, data_dict: typing.Dict):
    toolkit.check_access("emc_request_dataset_publication", context, data_dict)
    activity = create_dataset_management_activity(
        data_dict["pkg_id"], DatasetManagementActivityType.REQUEST_PUBLICATION
    )
    _ensure_user_is_notifiable(context["user"], data_dict["pkg_id"])
    toolkit.enqueue_job(
        jobs.notify_org_admins_of_dataset_management_request,
        args=[activity["id"]],
    )


def _ensure_user_is_notifiable(user_id: str, dataset_id):
    toolkit.get_action("emc_user_patch")(
        data_dict={"id": user_id, "activity_streams_email_notifications": True}
    )
    try:
        toolkit.get_action("follow_dataset")(
            data_dict={"id": dataset_id},
        )
    except toolkit.ValidationError:
        pass  # user is already following the dataset
