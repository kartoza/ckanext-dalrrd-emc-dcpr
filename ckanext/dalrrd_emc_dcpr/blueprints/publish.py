import json
from flask import Blueprint
from ckan.plugins import toolkit
import ckan.plugins as p
from ckan import model

publish_blueprint = Blueprint(
    "publish", __name__, template_folder="templates", url_prefix="/publish"
)


@publish_blueprint.route("/")
def index():
    return toolkit.render("publish.html")


@publish_blueprint.route("/reinstate/<package>")
def reinstate(package):
    package_dict = p.toolkit.get_action("package_show")({"model": model},{'id': package})
    package_dict["state"] = "active"
    p.toolkit.get_action('package_update')({"model": model}, package_dict)
    return json.dumps("success", indent=4)