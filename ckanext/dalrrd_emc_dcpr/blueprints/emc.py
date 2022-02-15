import logging
import typing

from flask import Blueprint

logger = logging.getLogger(__name__)

emc_blueprint = Blueprint(
    "emc", __name__, template_folder="templates", url_prefix="/emc"
)


@emc_blueprint.route("/request_package_maintenance")
def request_package_maintenance():
    logger.debug("Inside the emc request_package_maintenance view")
    result = f"<h1>Hi from the EMC request package maintenance page!</h1>"
    return result
