import logging

from flask import Blueprint
from ckan.plugins import toolkit
from ckan.lib.search import SearchError, SearchQueryError
import ckan.lib.helpers as h


logger = logging.getLogger(__name__)

dcpr_blueprint = Blueprint(
    "dcpr", __name__, template_folder="templates", url_prefix="/dcpr"
)


@dcpr_blueprint.route("/")
def dcpr_home():
    logger.debug("Inside the dcpr_home view")
    existing_requests = toolkit.get_action("dcpr_request_list")(data_dict={})

    return toolkit.render("dcpr/index.html", extra_vars={"requests": existing_requests})


@dcpr_blueprint.route("/search")
def dcpr_search():
    logger.debug("Inside the dcpr_search view")
    extra_vars = {}

    extra_vars[u"q"] = q = toolkit.request.args.get(u"q", u"")
    page = toolkit.h.get_page_number(toolkit.request.args)

    limit = toolkit.config.get(u"ckan.dcpr_requests_per_page") or 10
    data = {u"q": q, u"rows": limit, u"start": (page - 1) * limit}
    try:

        existing_requests = toolkit.get_action("dcpr_request_search")(data_dict=data)
        extra_vars["requests"] = existing_requests

        extra_vars[u"page"] = h.Page(
            collection=existing_requests[u"results"],
            page=page,
            item_count=existing_requests[u"count"],
            items_per_page=limit,
        )

    except SearchQueryError as error:
        logger.info("Request search query rejected: %r", error.args)
        toolkit.base.abort(
            400,
            "Invalid search query: {error_message}".format(error_message=str(error)),
        )
    except SearchError as error:
        # May be bad input from the user, but may also be more serious like
        # bad code causing a SOLR syntax error, or a problem connecting to
        # SOLR
        logger.error("Request search error: %r", error.args)
        extra_vars["query_error"] = True
        extra_vars["page"] = h.Page(collection=[])

    return toolkit.render("dcpr/index.html", extra_vars=extra_vars)
