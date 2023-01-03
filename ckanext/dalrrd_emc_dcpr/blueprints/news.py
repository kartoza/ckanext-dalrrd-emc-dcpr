from flask import Blueprint
from ckan.plugins import toolkit
import ckanext.pages.utils as utils
from .news_utils import list_news, news_edit_util, news_delete_util

news_blueprint = Blueprint(
    "news", __name__, template_folder="templates", url_prefix="/news"
)


@news_blueprint.route("/")
def index():
    list_news()
    return toolkit.render("news.html", type="news")


def news_show(page):
    return utils.pages_show(page, page_type="news")


def news_edit(page=None, data=None, errors=None, error_summary=None):
    return news_edit_util(page, data, errors, error_summary, "news")


def news_delete(page):
    return news_delete_util(page, page_type="news")


news_blueprint.add_url_rule("/news", view_func=index)
news_blueprint.add_url_rule(
    "/news_edit", view_func=news_edit, endpoint="news_new", methods=["GET", "POST"]
)
news_blueprint.add_url_rule("/news/<page>", view_func=news_show)
news_blueprint.add_url_rule(
    "/news_edit/", view_func=news_edit, endpoint="news_edit", methods=["GET", "POST"]
)
news_blueprint.add_url_rule(
    "/news_edit/<page>",
    view_func=news_edit,
    endpoint="news_edit",
    methods=["GET", "POST"],
)
news_blueprint.add_url_rule("/news/<page>", view_func=news_show)
news_blueprint.add_url_rule(
    "/news_delete/<page>",
    view_func=news_delete,
    endpoint="news_delete",
    methods=["GET", "POST"],
)
