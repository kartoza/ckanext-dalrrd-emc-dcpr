import logging

from ckan.plugins import toolkit
from flask import Blueprint

logger = logging.getLogger(__name__)

emc_blueprint = Blueprint(
    "emc", __name__, template_folder="templates", url_prefix="/emc"
)


@emc_blueprint.route("/request_dataset_maintenance/<dataset_id>")
def request_dataset_maintenance(dataset_id):
    toolkit.get_action("emc_request_dataset_maintenance")(
        data_dict={"pkg_id": dataset_id}
    )
    toolkit.h["flash_notice"](
        toolkit._(
            "Organization publishers have been notified of your request. You are now "
            "following the dataset and will be notified when it has been modified."
        )
    )
    return toolkit.redirect_to("dataset.read", id=dataset_id)


@emc_blueprint.route(
    "/request_dataset_management/<string:dataset_id>/<string:management_command>"
)
def request_dataset_management(dataset_id, management_command):
    action_name = {
        "maintenance": "emc_request_dataset_maintenance",
        "publication": "emc_request_dataset_publication",
    }[management_command]
    toolkit.get_action(action_name)(data_dict={"pkg_id": dataset_id})
    toolkit.h["flash_notice"](
        toolkit._(
            "Organization publishers have been notified of your request. You are now "
            "following the dataset and will be notified when it has been modified."
        )
    )
    return toolkit.redirect_to("dataset.read", id=dataset_id)
