from flask import Blueprint
from ckan.plugins import toolkit

publish_blueprint = Blueprint(
    "publish", __name__, template_folder="templates", url_prefix="/publish"
)


@publish_blueprint.route("/")
def index():
    return toolkit.render("publish.html")
