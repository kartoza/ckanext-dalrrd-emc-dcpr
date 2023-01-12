import json
import logging
import typing
from functools import partial
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.lib.helpers as h
import ckan.model
from flask import Blueprint, redirect, request
from flask.views import MethodView
from ckan.views.home import CACHE_PARAMETERS
from ckan.views.dataset import url_with_params
from ckan.plugins import toolkit
from ckan.logic import clean_dict, parse_params, tuplize_dict

from ..helpers import get_status_labels

logger = logging.getLogger(__name__)

error_report_blueprint = Blueprint(
    "error_report", __name__, template_folder="templates", url_prefix="/error_report"
)


@error_report_blueprint.route("/")
def get_error_reports():
    return _get_error_reports_list("error_report_list_public", True)


@error_report_blueprint.route("/rejected_error_reports")
def get_error_reports_list():
    return _get_error_reports_list("error_report_list_public")


@error_report_blueprint.route("/my_error_reports")
def get_my_error_reports():
    return _get_error_reports_list("my_error_report_list", True)


@error_report_blueprint.route("/submitted_error_reports")
def get_submitted_error_reports():
    return _get_error_reports_list("submitted_error_report_list", True)


def _request_url_(params_nopage, requests_type, q=None, page=None):
    params = list(params_nopage)
    params.append(("page", page))
    url = request.url_rule.rule

    return url_with_params(url, params)


def _get_error_reports_list(ckan_action: str, should_show_create_action: bool = False):
    try:
        error_reports = toolkit.get_action(ckan_action)(
            context={
                "user": toolkit.g.user,
                "dictize_for_ui": True,
            },
            data_dict={},
        )
    except toolkit.NotAuthorized:
        result = toolkit.abort(
            403,
            toolkit._("Not authorized to list error reports"),
        )

    else:
        params_nopage = [
            (k, v) for k, v in request.args.items(multi=True) if k != "page"
        ]
        params_nosort = [(k, v) for k, v in params_nopage]
        pager_url = partial(_request_url_, params_nosort, None)
        page = h.get_page_number(request.args)
        extra_vars = {
            "error_reports": error_reports,
            "statuses": get_status_labels(),
            "show_create_button": should_show_create_action,
            "page": h.Page(
                collection=error_reports,
                items_per_page=20,
                url=pager_url,
                page=page,
                item_count=len(error_reports),
            ),
        }
        result = toolkit.render("error_report/list.html", extra_vars=extra_vars)
    return result


class ErrorReportCreateView(MethodView):
    def get(self, data=None, errors=None, error_summary=None):
        toolkit.check_access("error_report_create_auth", {"user": toolkit.g.user})
        data_to_show = data or clean_dict(
            dict_fns.unflatten(
                tuplize_dict(parse_params(request.args, ignore_keys=CACHE_PARAMETERS))
            )
        )
        packages = ckan.model.Session.query(ckan.model.Package).all()

        metadata_records = [
            {"value": record.id, "text": record.title} for record in packages
        ]

        selected_metadata_record = request.args.get("metadata_record", None)

        extra_vars = {
            "form_snippet": "error_report/snippets/report_form.html",
            "enable_owner_fieldset": True,
            "enable_nsif_fieldset": False,
            "csi_reference_id": None,
            "data": data_to_show,
            "metadata_records": metadata_records,
            "selected_record": selected_metadata_record,
            "errors": errors or {},
            "error_summary": error_summary or {},
        }
        return toolkit.render("error_report/edit.html", extra_vars=extra_vars)

    def post(self):
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
        except dict_fns.DataError:
            result = toolkit.abort(
                400, toolkit._("Integrity Error, problem in parsing form parameters")
            )
        else:
            if data_dict.get("metadata_record") is None:
                data_dict["metadata_record"] = request.args.get("metadata_record")
            try:
                data_dict["owner_user"] = toolkit.g.user
                error_report = toolkit.get_action("error_report_create")(
                    context={
                        "user": toolkit.g.user,
                        "auth_user_obj": toolkit.g.userobj,
                    },
                    data_dict=data_dict,
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("Error report not found"))
            except toolkit.ValidationError as exc:
                errors = exc.error_dict
                error_summary = exc.error_summary
                result = self.get(
                    data=data_dict, errors=errors, error_summary=error_summary
                )
            else:
                url = toolkit.h.url_for(
                    "error_report.error_report_show",
                    csi_reference_id=error_report["csi_reference_id"],
                )
                result = toolkit.h.redirect_to(url)
        return result


new_error_report_view = ErrorReportCreateView.as_view("new_error_report")
error_report_blueprint.add_url_rule("/new/", view_func=new_error_report_view)
#
#


class ErrorReportUpdateView(MethodView):
    show_action = "error_report_show"
    success_redirect_to_view = "error_report.error_report_show"
    update_auth: typing.Optional[str] = None
    update_action: typing.Optional[str] = None
    template_path = "error_report/edit.html"
    form_snippet = "error_report/snippets/report_form.html"
    enable_owner_fieldset = True
    enable_nsif_fieldset = False

    def get(
        self,
        csi_reference_id: str,
        data: typing.Optional[typing.Dict] = None,
        errors: typing.Optional[typing.Dict] = None,
        error_summary=None,
    ):
        context = _prepare_context()
        try:
            old_data = toolkit.get_action(self.show_action)(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
            if data is not None:
                old_data.update(data)
            data = old_data

            packages = ckan.model.Session.query(ckan.model.Package).all()

            metadata_records = [
                {"value": record.id, "text": record.title} for record in packages
            ]
            selected_metadata_record = request.args.get("metadata_record", None)
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            result = toolkit.abort(404, toolkit._("Error report not found"))
        else:
            try:
                toolkit.check_access(
                    self.update_auth,
                    context,
                    data_dict={"csi_reference_id": csi_reference_id},
                )
            except toolkit.NotAuthorized:
                result = toolkit.abort(
                    403,
                    toolkit._("User %r not authorized to edit %s")
                    % (toolkit.g.user, csi_reference_id),
                )
            else:
                result = toolkit.render(
                    self.template_path,
                    extra_vars={
                        "form_snippet": self.form_snippet,
                        "enable_owner_fieldset": self.enable_owner_fieldset,
                        "enable_nsif_fieldset": self.enable_nsif_fieldset,
                        "data": data,
                        "metadata_records": metadata_records,
                        "selected_record": selected_metadata_record,
                        "csi_reference_id": csi_reference_id,
                        "errors": errors or {},
                        "error_summary": error_summary or {},
                    },
                )
        return result

    def post(self, csi_reference_id: str):
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
            data_dict["csi_reference_id"] = csi_reference_id
        except dict_fns.DataError:
            result = toolkit.abort(400, toolkit._("Integrity Error"))
        else:
            context = _prepare_context()
            try:
                toolkit.get_action(self.update_action)(context, data_dict)
            except toolkit.NotAuthorized as exc:
                result = toolkit.base.abort(
                    403,
                    toolkit._("Unauthorized to update error report, %s") % exc,
                )
            except toolkit.ObjectNotFound:
                result = toolkit.base.abort(404, toolkit._("Error report not found"))
            except toolkit.ValidationError as exc:
                errors = exc.error_dict
                error_summary = exc.error_summary
                result = self.get(
                    csi_reference_id,
                    data=data_dict,
                    errors=errors,
                    error_summary=error_summary,
                )
            else:
                url = toolkit.h.url_for(
                    self.success_redirect_to_view, csi_reference_id=csi_reference_id
                )
                result = toolkit.h.redirect_to(url)
        return result


class ErrorReportOwnerUpdateView(ErrorReportUpdateView):
    update_auth = "error_report_update_by_owner_auth"
    update_action = "error_report_update_by_owner"
    enable_owner_fieldset = True
    enable_nsif_fieldset = False


# came back here to feature data in the EMC
class ErrorReportNsifUpdateView(ErrorReportUpdateView):
    update_auth = "error_report_update_by_nsif_auth"
    update_action = "error_report_update_by_nsif"
    enable_owner_fieldset = False
    enable_nsif_fieldset = True


owner_edit_error_report_view = ErrorReportOwnerUpdateView.as_view(
    "owner_edit_error_report"
)
error_report_blueprint.add_url_rule(
    "/<csi_reference_id>/owner_edit/",
    view_func=owner_edit_error_report_view,
)

nsif_edit_error_report_view = ErrorReportNsifUpdateView.as_view(
    "nsif_edit_error_report"
)
error_report_blueprint.add_url_rule(
    "/<csi_reference_id>/nsif_edit/", view_func=nsif_edit_error_report_view
)

#
# error_report show page


@error_report_blueprint.route("/show/<csi_reference_id>")
def error_report_show(csi_reference_id):
    try:
        error_report = toolkit.get_action("error_report_show")(
            context={"dictize_for_ui": True},
            data_dict={"csi_reference_id": csi_reference_id},
        )
    except toolkit.ObjectNotFound:
        result = toolkit.abort(404, toolkit._("Error report not found"))
    except toolkit.NotAuthorized:
        result = toolkit.base.abort(401, toolkit._("Not authorized"))
    else:
        extra_vars = {
            "error_report": error_report,
        }
        result = toolkit.render("error_report/show.html", extra_vars=extra_vars)
    return result


class ErrorReportModerateView(MethodView):
    template_name = "error_report/moderate.html"
    actions = {
        "nsif": {
            "message": "Moderate error report on behalf of NSIF",
            "ckan_action": "error_report_nsif_moderate",
        }
    }

    def get(self, csi_reference_id: str):
        context = _prepare_context()
        try:
            error_report = toolkit.get_action("error_report_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            result = toolkit.abort(404, toolkit._("Error report not found"))
        except toolkit.NotAuthorized:
            result = toolkit.abort(
                403, toolkit._("Unauthorized to moderate error report")
            )
        else:
            result = toolkit.render(
                self.template_name,
                extra_vars={
                    "error_report": error_report,
                    "action": self.actions.get("nsif", {}).get("message"),
                    "action_url": toolkit.h["url_for"](
                        "error_report.error_report_moderate",
                        csi_reference_id=csi_reference_id,
                    ),
                },
            )
        return result

    def post(self, csi_reference_id: str):
        data_dict = {
            "csi_reference_id": csi_reference_id,
            "action": list(request.form.keys())[0],
        }
        try:
            ckan_action = self.actions.get("nsif", {}).get("ckan_action")
            logger.info(f" ckan action {ckan_action}")
            toolkit.get_action(ckan_action)(_prepare_context(), data_dict=data_dict)
        except toolkit.ObjectNotFound:
            result = toolkit.abort(404, toolkit._("Report not found"))
        except toolkit.NotAuthorized:
            result = toolkit.abort(
                403, toolkit._("Unauthorized to submit moderation for error report")
            )
        else:
            toolkit.h["flash_notice"](toolkit._("Moderation submitted"))
            result = toolkit.redirect_to(
                toolkit.h["url_for"](
                    "error_report.error_report_show", csi_reference_id=csi_reference_id
                )
            )
        return result


moderate_error_report_view = ErrorReportModerateView.as_view("error_report_moderate")
error_report_blueprint.add_url_rule(
    "/<csi_reference_id>/moderate/",
    view_func=moderate_error_report_view,
)


class ErrorReportDeleteView(MethodView):
    def get(self, csi_reference_id: str):
        context = _prepare_context()
        try:
            error_report = toolkit.get_action("error_report_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            return toolkit.abort(404, toolkit._("Error report not found"))
        except toolkit.NotAuthorized:
            return toolkit.abort(403, toolkit._("Unauthorized to delete error report"))
        return toolkit.render(
            "error_report/ask_for_confirmation.html",
            extra_vars={
                "error_report": error_report,
                "action": "delete",
                "action_url": toolkit.h["url_for"](
                    "error_report.error_report_delete",
                    csi_reference_id=csi_reference_id,
                ),
            },
        )

    def post(self, csi_reference_id: str):
        if "cancel" not in request.form.keys():
            context = _prepare_context()
            try:
                toolkit.get_action("error_report_delete")(
                    context, data_dict={"csi_reference_id": csi_reference_id}
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("Error report not found"))
            except toolkit.NotAuthorized:
                result = toolkit.abort(
                    403, toolkit._("Unauthorized to delete error report %s") % ""
                )
            else:
                toolkit.h["flash_notice"](toolkit._("Error report has been deleted."))
                result = toolkit.redirect_to(
                    toolkit.h["url_for"]("error_report.get_error_reports")
                )
        else:
            result = toolkit.h.redirect_to(
                toolkit.h["url_for"](
                    "error_report.error_report_show", csi_reference_id=csi_reference_id
                )
            )
        return result


delete_error_report_view = ErrorReportDeleteView.as_view("error_report_delete")
error_report_blueprint.add_url_rule(
    "/<csi_reference_id>/delete/", view_func=delete_error_report_view
)


def _prepare_context() -> typing.Dict:
    context = {
        "model": ckan.model,
        "session": ckan.model.Session,
        "user": toolkit.g.user,
        "auth_user_obj": toolkit.g.userobj,
    }
    return context
