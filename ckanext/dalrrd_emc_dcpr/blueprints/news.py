from flask import Blueprint
from ckan.plugins import toolkit

news_blueprint = Blueprint(
    "news", __name__, template_folder="templates", url_prefix="/news"
)


@news_blueprint.route("/")
def index():
    return toolkit.render("news.html")
