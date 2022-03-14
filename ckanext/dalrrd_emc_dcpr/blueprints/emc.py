import logging
import typing

from ckan import model
from ckan.logic.schema import default_create_activity_schema
from ckan.plugins import toolkit
from flask import Blueprint

logger = logging.getLogger(__name__)

emc_blueprint = Blueprint(
    "emc", __name__, template_folder="templates", url_prefix="/emc"
)


@emc_blueprint.route("/request_dataset_maintenance/<dataset_id>")
def request_dataset_maintenance(dataset_id):
    logger.debug(f"{locals()=}")
    logger.debug("Inside the emc request_package_maintenance view")
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

    logger.debug(f"{activity_schema=}")
    toolkit.get_action("activity_create")(
        context={
            "ignore_auth": True,
            "schema": activity_schema,
        },
        data_dict={
            "user_id": toolkit.g.userobj.id,
            "object_id": dataset_id,
            "activity_type": "requested modification",
            "data": None,
        },
    )

    toolkit.h["flash_success"](
        toolkit._("Sent notification to the dataset publishers!")
    )
    return toolkit.redirect_to("dataset.read", id=dataset_id)
