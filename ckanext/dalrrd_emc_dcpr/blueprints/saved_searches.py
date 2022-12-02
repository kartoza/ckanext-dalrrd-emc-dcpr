from flask import Blueprint
from ckan.plugins import toolkit

saved_searches_blueprint = Blueprint(
    "saved_searches",
    __name__,
    template_folder="templates",
    url_prefix="/saved_searches",
)


@saved_searches_blueprint.route("/")
def index():
    return toolkit.render("saved_searches.html")
