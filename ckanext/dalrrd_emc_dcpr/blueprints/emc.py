import logging

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
    toolkit.get_action("emc_request_dataset_maintenance")(
        data_dict={"pkg_id": dataset_id}
    )
    toolkit.h["flash_notice"](
        toolkit._(
            "Organization publishers will be notified of your request to perform "
            "maintenance on this dataset!"
        )
    )
    return toolkit.redirect_to("dataset.read", id=dataset_id)
