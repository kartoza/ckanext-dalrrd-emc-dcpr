import logging

from flask import Blueprint
from ckan.plugins import toolkit

logger = logging.getLogger(__name__)

dcpr_blueprint = Blueprint(
    "dcpr", __name__, template_folder="templates", url_prefix="/dcpr"
)


@dcpr_blueprint.route("/")
def dcpr_home():
    logger.debug("Inside the dcpr_home view")
    existing_requests = toolkit.get_action("dcpr_request_list")(data_dict={})

    return toolkit.render("dcpr/index.html", extra_vars={"requests": existing_requests})
