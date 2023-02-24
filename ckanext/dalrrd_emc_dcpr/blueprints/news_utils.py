import ckantoolkit as tk
import ckan.lib.helpers as helpers
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns


config = tk.config
_ = tk._


def list_news():
    tk.c.pages_dict = tk.get_action("ckanext_pages_list")(
        context={}, data_dict={"page_type": "news"}
    )
    tk.c.page = helpers.Page(
        collection=tk.c.pages_dict,
        page=tk.request.params.get("page", 1),
        url=helpers.pager_url,
        items_per_page=21,
    )

    # return tk.render('ckanext_pages/blog_list.html')


def news_edit_util(
    page=None, data=None, errors=None, error_summary=None, page_type="pages"
):

    page_dict = None
    if page:
        if page.startswith("/"):
            page = page[1:]
        page_dict = tk.get_action("ckanext_pages_show")(
            context={}, data_dict={"org_id": None, "page": page}
        )
    if page_dict is None:
        page_dict = {}
    if tk.request.method == "POST" and not data:
        data = _parse_form_data(tk.request)

        page_dict.update(data)

        page_dict["org_id"] = None
        page_dict["page"] = page
        page_dict["page_type"] = "page" if page_type == "pages" else page_type

        try:
            tk.get_action("ckanext_pages_update")(context={}, data_dict=page_dict)
        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            tk.h.flash_error(error_summary)
            return news_edit_util(
                page, data, errors, error_summary, page_type=page_type
            )

        endpoint = "news.news_show"
        # tk.redirect_to(endpoint, page='/' + page_dict['name'])
        return tk.redirect_to("/news")
    try:
        tk.check_access("ckanext_pages_update", {"user": tk.c.user or tk.c.author})
    except tk.NotAuthorized:
        return tk.abort(401, _("Unauthorized to create or edit a page"))

    if not data:
        data = page_dict

    errors = errors or {}
    error_summary = error_summary or {}

    form_snippet = config.get("ckanext.pages.form", "ckanext_pages/base_form.html")

    vars = {
        "data": data,
        "errors": errors,
        "error_summary": error_summary,
        "page": page or "",
        "form_snippet": form_snippet,
    }

    return tk.render("ckanext_pages/%s_edit.html" % page_type, extra_vars=vars)


def news_delete_util(page, page_type="pages"):
    if page.startswith("/"):
        page = page[1:]
    if "cancel" in tk.request.params:
        tk.redirect_to("%s_edit" % page_type, page="/" + page)
    try:
        if tk.request.method == "POST":
            tk.get_action("ckanext_pages_delete")({}, {"page": page})
            return tk.redirect_to("/news")
        else:
            return tk.abort(404, _("Page Not Found"))
    except tk.NotAuthorized:
        return tk.abort(401, _("Unauthorized to delete page"))
    except tk.ObjectNotFound:
        return tk.abort(404, _("Group not found"))
    return tk.render("ckanext_pages/confirm_delete.html", {"page": page})


def _parse_form_data(request):
    form_data = request.form
    return logic.clean_dict(
        dict_fns.unflatten(logic.tuplize_dict(logic.parse_params(form_data)))
    )
