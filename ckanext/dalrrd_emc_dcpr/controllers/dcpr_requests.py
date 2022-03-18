import ckan.plugins.toolkit as toolkit


log = __import__("logging").getLogger(__name__)


class DCPRRequestsController(toolkit.BaseController):
    def index(self):
        try:
            requests = toolkit.get_action("dcpr_requests_list")({}, {})
        except toolkit.NotAuthorized:
            toolkit.abort(401)

        return toolkit.render("dcpr/index.html", extra_vars={"requests": requests})
