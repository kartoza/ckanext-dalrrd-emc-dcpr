import json
import logging
import typing
from functools import partial
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.lib.helpers as h
from ckan.common import config
import ckan.model
from flask import Blueprint, redirect, request
from flask.views import MethodView
from ckan.views.home import CACHE_PARAMETERS
from ckan.views.dataset import url_with_params
from ckan.plugins import toolkit
from ckan.logic import clean_dict, parse_params, tuplize_dict

from .. import constants
from ..helpers import get_status_labels
from ..model.dcpr_request import DCPRRequestUrgency
from ..model.dcpr_request import DCPRCaptureMethod, DCPRTOPICCATEGORY, DCPRCHARACTERSET


logger = logging.getLogger(__name__)

dcpr_blueprint = Blueprint(
    "dcpr", __name__, template_folder="templates", url_prefix="/dcpr"
)


@dcpr_blueprint.route("/")
def index():
    return toolkit.render("data_capture.html")


@dcpr_blueprint.route("/public")
def get_public_dcpr_requests():
    return _get_dcpr_request_list("dcpr_request_list_public")


@dcpr_blueprint.route("/my-dcpr-requests")
def get_my_dcpr_requests():
    return _get_dcpr_request_list(
        "my_dcpr_request_list", should_show_create_action=True
    )


@dcpr_blueprint.route("/awaiting-nsif-moderation-dcpr-requests")
def get_awaiting_nsif_moderation_dcpr_requests():
    return _get_dcpr_request_list("dcpr_request_list_awaiting_nsif_moderation")


@dcpr_blueprint.route("/awaiting-csi-moderation-dcpr-requests")
def get_awaiting_csi_moderation_dcpr_requests():
    return _get_dcpr_request_list("dcpr_request_list_awaiting_csi_moderation")


@dcpr_blueprint.route("/under-preparation-dcpr-requests")
def get_under_preparation_dcpr_requests():
    return _get_dcpr_request_list("dcpr_request_list_under_preparation")


def _request_url_(params_nopage, requests_type, q=None, page=None):
    params = list(params_nopage)
    params.append(("page", page))
    url = request.url_rule.rule

    return url_with_params(url, params)


def _get_dcpr_request_list(ckan_action: str, should_show_create_action: bool = False):
    try:
        dcpr_requests = toolkit.get_action(ckan_action)(
            context={
                "user": toolkit.g.user,
                "dictize_for_ui": True,
            },
            data_dict={},
        )
    except toolkit.NotAuthorized:
        result = toolkit.abort(
            403,
            toolkit._("Not authorized to list DCPR requests"),
        )

    else:
        params_nopage = [
            (k, v) for k, v in request.args.items(multi=True) if k != "page"
        ]
        params_nosort = [(k, v) for k, v in params_nopage]
        pager_url = partial(_request_url_, params_nosort, None)
        page = h.get_page_number(request.args)
        extra_vars = {
            "dcpr_requests": dcpr_requests,
            "statuses": get_status_labels(),
            "show_create_button": should_show_create_action,
            "page": h.Page(
                collection=dcpr_requests,
                items_per_page=20,
                url=pager_url,
                page=page,
                item_count=len(dcpr_requests),
            ),
        }
        result = toolkit.render("dcpr/list.html", extra_vars=extra_vars)
    return result


class DcprRequestCreateView(MethodView):
    def get(self, data=None, errors=None, error_summary=None, type=None):
        toolkit.check_access("dcpr_request_create_auth", {"user": toolkit.g.user})
        data_to_show = data or clean_dict(
            dict_fns.unflatten(
                tuplize_dict(parse_params(request.args, ignore_keys=CACHE_PARAMETERS))
            )
        )
        if "organization_id" not in request.args:
            # if we don't already have an org id, need to let user choose from those orgs where she is a member
            current_memberships = (
                ckan.model.Session.query(ckan.model.Group)
                .filter(ckan.model.Group.is_organization)
                .all()
            )
            relevant_orgs = [
                {"value": org.id, "text": org.name} for org in current_memberships
            ]
            # else:
            #     current_memberships = toolkit.h["emc_org_memberships"](
            #         toolkit.g.userobj.id
            #     )
            #     relevant_orgs = [
            #         {"value": org.id, "text": org.name}
            #         for org, _ in current_memberships
            #     ]
        else:
            # if we have an org id in request.args then there is no need to show the orgs select
            relevant_orgs = None

        serialized_errors = json.dumps(errors or {})
        serialized_error_summary = json.dumps(error_summary or {})
        extra_vars = {
            "form_snippet": "dcpr/snippets/request_form.html",
            "enable_owner_fieldset": True,
            "enable_nsif_fieldset": False,
            "enable_csi_fieldset": False,
            "csi_reference_id": None,
            "data": data_to_show,
            "errors": errors or {},
            "error_summary": error_summary or {},
            "relevant_organizations": relevant_orgs,
            "data_urgency_options": [
                {"value": level.value, "text": level.value}
                for level in DCPRRequestUrgency
            ],
            "dataset_capture_method_options": [
                {"value": capture_method.value, "text": capture_method.value}
                for capture_method in DCPRCaptureMethod
            ],
            "topic_categories": [
                {"value": topic.value, "text": topic.value}
                for topic in DCPRTOPICCATEGORY
            ],
            "charactersets": [
                {"value": char.value, "text": char.value} for char in DCPRCHARACTERSET
            ]
            # TODO: perhaps we can provide the name of the form that will be shown, as it will presumably be
            #  different according with the user role
        }
        return toolkit.render("dcpr/edit.html", extra_vars=extra_vars)

    def post(self, type=None):
        try:
            flat_data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
            # these the submitted requests form fields with the data
            data_dict = _unflatten_dcpr_request_datasets(flat_data_dict)
        except dict_fns.DataError:
            result = toolkit.abort(400, toolkit._("Integrity Error"))
        else:
            if data_dict.get("organization_id") is None:
                data_dict["organization_id"] = request.args.get("organization_id")
            try:
                dcpr_request = toolkit.get_action("dcpr_request_create")(
                    context={
                        "user": toolkit.g.user,
                        "auth_user_obj": toolkit.g.userobj,
                    },
                    data_dict=data_dict,
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("DCPR request not found"))
            except toolkit.ValidationError as exc:
                errors = exc.error_dict
                error_summary = exc.error_summary
                result = self.get(
                    data=data_dict, errors=errors, error_summary=error_summary
                )
            else:
                url = toolkit.h.url_for(
                    "dcpr.dcpr_request_show",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                )
                result = toolkit.h.redirect_to(url)
        return result


new_dcpr_request_view = DcprRequestCreateView.as_view("new_dcpr_request")
dcpr_blueprint.add_url_rule("/request/new/<type>", view_func=new_dcpr_request_view)


class _DcprUpdateView(MethodView):
    show_action = "dcpr_request_show"
    success_redirect_to_view = "dcpr.dcpr_request_show"
    update_auth: typing.Optional[str] = None
    update_action: typing.Optional[str] = None
    template_path = "dcpr/edit.html"
    form_snippet = "dcpr/snippets/request_form.html"
    enable_owner_fieldset = True
    enable_nsif_fieldset = False
    enable_csi_fieldset = False

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
            # old data is from the database and data is passed from the
            # user. if there is a validation error. Use user's data, if there.
            if data is not None:
                old_data.update(data)
            data = old_data
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            result = toolkit.abort(404, toolkit._("Dataset not found"))
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
                        "enable_csi_fieldset": self.enable_csi_fieldset,
                        "data": data,
                        "csi_reference_id": csi_reference_id,
                        "errors": errors or {},
                        "error_summary": error_summary or {},
                        "data_urgency_options": [
                            {"value": level.value, "text": level.value}
                            for level in DCPRRequestUrgency
                        ],
                        "dataset_capture_method_options": [
                            {
                                "value": capture_method.value,
                                "text": capture_method.value,
                            }
                            for capture_method in DCPRCaptureMethod
                        ],
                        "topic_categories": [
                            {"value": topic.value, "text": topic.value}
                            for topic in DCPRTOPICCATEGORY
                        ],
                        "charactersets": [
                            {"value": char.value, "text": char.value}
                            for char in DCPRCHARACTERSET
                        ],
                    },
                )
        return result

    def post(self, csi_reference_id: str):
        try:
            flat_data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
            data_dict = _unflatten_dcpr_request_datasets(flat_data_dict)
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
                    toolkit._("Unauthorized to update DCPR request, %s") % exc,
                )
            except toolkit.ObjectNotFound:
                result = toolkit.base.abort(404, toolkit._("DCPR request not found"))
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


class DcprRequestOwnerUpdateView(_DcprUpdateView):
    update_auth = "dcpr_request_update_by_owner_auth"
    update_action = "dcpr_request_update_by_owner"
    enable_owner_fieldset = True
    enable_nsif_fieldset = False
    enable_csi_fieldset = False


# came back here to feature data in the EMC
class DcprRequestNsifUpdateView(_DcprUpdateView):
    update_auth = "dcpr_request_update_by_nsif_auth"
    update_action = "dcpr_request_update_by_nsif"
    enable_owner_fieldset = False
    enable_nsif_fieldset = True
    enable_csi_fieldset = False


class DcprRequestCsifUpdateView(_DcprUpdateView):
    update_auth = "dcpr_request_update_by_csi_auth"
    update_action = "dcpr_request_update_by_csi"
    enable_owner_fieldset = False
    enable_nsif_fieldset = False
    enable_csi_fieldset = True


owner_edit_dcpr_request_view = DcprRequestOwnerUpdateView.as_view(
    "owner_edit_dcpr_request"
)
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/owner_edit/", view_func=owner_edit_dcpr_request_view
)

nsif_edit_dcpr_request_view = DcprRequestNsifUpdateView.as_view(
    "nsif_edit_dcpr_request"
)
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/nsif_edit/", view_func=nsif_edit_dcpr_request_view
)

csi_edit_dcpr_request_view = DcprRequestCsifUpdateView.as_view("csi_edit_dcpr_request")
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/csi_edit/", view_func=csi_edit_dcpr_request_view
)


# request show page
@dcpr_blueprint.route("/request/<csi_reference_id>")
def dcpr_request_show(csi_reference_id):
    try:
        dcpr_request = toolkit.get_action("dcpr_request_show")(
            context={"dictize_for_ui": True},
            data_dict={"csi_reference_id": csi_reference_id},
        )
    except toolkit.ObjectNotFound:
        result = toolkit.abort(404, toolkit._("DCPR request not found"))
    except toolkit.NotAuthorized:
        result = toolkit.base.abort(401, toolkit._("Not authorized"))
    else:
        extra_vars = {
            "dcpr_request": dcpr_request,
        }
        result = toolkit.render("dcpr/show.html", extra_vars=extra_vars)
    return result


class DcprRequestModerateView(MethodView):
    template_name = "dcpr/moderate.html"
    actions = {
        "nsif": {
            "message": "Moderate DCPR request on behalf of NSIF",
            "ckan_action": "dcpr_request_nsif_moderate",
        },
        "csi": {
            "message": "Moderate DCPR request on behalf of CSI",
            "ckan_action": "dcpr_request_csi_moderate",
        },
    }

    def get(self, csi_reference_id: str, organization: str):
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            result = toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            result = toolkit.abort(
                403, toolkit._("Unauthorized to moderate DCPR request")
            )
        else:
            result = toolkit.render(
                self.template_name,
                extra_vars={
                    "dcpr_request": dcpr_request,
                    "action": self.actions.get(organization, {}).get("message"),
                    "action_url": toolkit.h["url_for"](
                        "dcpr.dcpr_request_moderate",
                        csi_reference_id=csi_reference_id,
                        organization=organization,
                    ),
                },
            )
        return result

    def post(self, csi_reference_id: str, organization: str):
        data_dict = {
            "csi_reference_id": csi_reference_id,
            "action": list(request.form.keys())[0],
        }
        try:
            ckan_action = self.actions.get(organization, {}).get("ckan_action")
            toolkit.get_action(ckan_action)(_prepare_context(), data_dict=data_dict)
        except toolkit.ObjectNotFound:
            result = toolkit.abort(404, toolkit._("Dataset not found"))
        except toolkit.NotAuthorized:
            result = toolkit.abort(
                403, toolkit._("Unauthorized to submit moderation for DCPR request")
            )
        else:
            toolkit.h["flash_notice"](toolkit._("Moderation submitted"))
            result = toolkit.redirect_to(
                toolkit.h["url_for"](
                    "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                )
            )
        return result


moderate_dcpr_request_view = DcprRequestModerateView.as_view("dcpr_request_moderate")
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/moderate/<organization>",
    view_func=moderate_dcpr_request_view,
)


class DcprRequestSubmitView(MethodView):
    def get(self, csi_reference_id: str):
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            result = toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            result = toolkit.abort(
                403, toolkit._("Unauthorized to submit DCPR request")
            )
        else:
            result = toolkit.render(
                "dcpr/ask_for_confirmation.html",
                extra_vars={
                    "dcpr_request": dcpr_request,
                    "action": "submit",
                    "action_url": toolkit.h["url_for"](
                        "dcpr.dcpr_request_submit", csi_reference_id=csi_reference_id
                    ),
                },
            )
        return result

    def post(self, csi_reference_id: str):
        if "cancel" not in request.form.keys():
            context = _prepare_context()
            try:
                toolkit.get_action("dcpr_request_submit")(
                    context, data_dict={"csi_reference_id": csi_reference_id}
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("Dataset not found"))
            except toolkit.NotAuthorized:
                result = toolkit.abort(
                    403, toolkit._("Unauthorized to submit package %s") % ""
                )
            else:
                toolkit.h["flash_notice"](toolkit._("Dataset has been submitted!"))
                result = toolkit.redirect_to(
                    toolkit.h["url_for"](
                        "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                    )
                )
        else:
            result = toolkit.h.redirect_to(
                toolkit.h["url_for"](
                    "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                )
            )
        return result


submit_dcpr_request_view = DcprRequestSubmitView.as_view("dcpr_request_submit")
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/submit/", view_func=submit_dcpr_request_view
)


class DcprRequestDeleteView(MethodView):
    def get(self, csi_reference_id: str):
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            return toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            return toolkit.abort(403, toolkit._("Unauthorized to delete DCPR request"))
        return toolkit.render(
            "dcpr/ask_for_confirmation.html",
            extra_vars={
                "dcpr_request": dcpr_request,
                "action": "delete",
                "action_url": toolkit.h["url_for"](
                    "dcpr.dcpr_request_delete", csi_reference_id=csi_reference_id
                ),
            },
        )

    def post(self, csi_reference_id: str):
        if "cancel" not in request.form.keys():
            context = _prepare_context()
            try:
                toolkit.get_action("dcpr_request_delete")(
                    context, data_dict={"csi_reference_id": csi_reference_id}
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("DCPR request not found"))
            except toolkit.NotAuthorized:
                result = toolkit.abort(
                    403, toolkit._("Unauthorized to delete DCPR request %s") % ""
                )
            else:
                toolkit.h["flash_notice"](toolkit._("DCPR request has been deleted."))
                result = toolkit.redirect_to(
                    toolkit.h["url_for"]("dcpr.get_my_dcpr_requests")
                )
        else:
            result = toolkit.h.redirect_to(
                toolkit.h["url_for"](
                    "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                )
            )
        return result


delete_dcpr_request_view = DcprRequestDeleteView.as_view("dcpr_request_delete")
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/delete/", view_func=delete_dcpr_request_view
)


class DcprRequestResignReviewerView(MethodView):
    def get(self, csi_reference_id: str, organization: str):
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            return toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            return toolkit.abort(
                403,
                toolkit._(
                    "Unauthorized to resign from the role of reviewer of DCPR request"
                ),
            )
        action = {
            "nsif": "Resign from being the NSIF reviewer",
            "csi": "Resign from being the CSI reviewer",
        }.get(organization)
        return toolkit.render(
            "dcpr/ask_for_confirmation.html",
            extra_vars={
                "dcpr_request": dcpr_request,
                "action": action,
                "action_url": toolkit.h["url_for"](
                    "dcpr.dcpr_request_resign_reviewer",
                    csi_reference_id=csi_reference_id,
                    organization=organization,
                ),
            },
        )

    def post(self, csi_reference_id: str, organization: str):
        if "cancel" not in request.form.keys():
            context = _prepare_context()
            action_name = {
                "nsif": "resign_dcpr_request_nsif_reviewer",
                "csi": "resign_dcpr_request_csi_reviewer",
            }.get(organization)
            try:
                toolkit.get_action(action_name)(
                    context, data_dict={"csi_reference_id": csi_reference_id}
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("Dataset not found"))
            except toolkit.NotAuthorized:
                result = toolkit.abort(
                    403,
                    toolkit._(
                        "Unauthorized to resign from the role of DCPR request reviewer"
                    ),
                )
            else:
                toolkit.h["flash_notice"](
                    toolkit._("You are no longer the reviewer for the DCPR request.")
                )
                result = toolkit.redirect_to(
                    toolkit.h["url_for"](
                        "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                    )
                )
        else:
            result = toolkit.h.redirect_to(
                toolkit.h["url_for"](
                    "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                )
            )
        return result


resign_dcpr_request_view = DcprRequestResignReviewerView.as_view(
    "dcpr_request_resign_reviewer"
)
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/resign/<organization>",
    view_func=resign_dcpr_request_view,
)


class DcprRequestBecomeReviewerView(MethodView):
    def get(self, csi_reference_id: str, organization: str):
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            result = toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            result = toolkit.abort(
                403, toolkit._("Unauthorized to become the reviewer for DCPR request")
            )
        else:
            action = {
                constants.NSIF_ORG_NAME: "become NSIF reviewer",
                constants.CSI_ORG_NAME: "become CSI reviewer",
            }.get(organization)
            result = toolkit.render(
                "dcpr/ask_for_confirmation.html",
                extra_vars={
                    "dcpr_request": dcpr_request,
                    "action": action,
                    "action_url": toolkit.h["url_for"](
                        "dcpr.dcpr_request_become_reviewer",
                        csi_reference_id=csi_reference_id,
                        organization=organization,
                    ),
                },
            )
        return result

    def post(self, csi_reference_id: str, organization: str):
        if "cancel" not in request.form.keys():
            context = _prepare_context()
            action_name = {
                "nsif": "claim_dcpr_request_nsif_reviewer",
                "csi": "claim_dcpr_request_csi_reviewer",
            }.get(organization)
            try:
                toolkit.get_action(action_name)(
                    context, data_dict={"csi_reference_id": csi_reference_id}
                )
            except toolkit.ObjectNotFound:
                result = toolkit.abort(404, toolkit._("Dataset not found"))
            except toolkit.NotAuthorized:
                result = toolkit.abort(
                    403, toolkit._("Unauthorized to claim DCPR request")
                )
            else:
                toolkit.h["flash_notice"](
                    toolkit._("You are now the reviewer for the DCPR request.")
                )
                result = toolkit.redirect_to(
                    toolkit.h["url_for"](
                        "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                    )
                )
        else:
            result = toolkit.h.redirect_to(
                toolkit.h["url_for"](
                    "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
                )
            )
        return result


claim_dcpr_request_view = DcprRequestBecomeReviewerView.as_view(
    "dcpr_request_become_reviewer"
)
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/review/<organization>",
    view_func=claim_dcpr_request_view,
)


def _prepare_context() -> typing.Dict:
    context = {
        "model": ckan.model,
        "session": ckan.model.Session,
        "user": toolkit.g.user,
        "auth_user_obj": toolkit.g.userobj,
    }
    return context


def _unflatten_dcpr_request_datasets(flat_data_dict: typing.Dict) -> typing.Dict:
    dataset_fields = [
        "proposed_dataset_title",
        "dataset_purpose",
        "dataset_custodian",
        "data_type",
        "proposed_abstract",
        "lineage_statement",
        "associated_attributes",
        "data_usage_restrictions",
        "capture_method",
        "topic_category",
        "dataset_characterset",
        "metadata_characterset",
    ]
    # how many datasets have been submitted?'
    first_ds_field_value = flat_data_dict.get(dataset_fields[0])
    num_datasets = (
        len(first_ds_field_value) - 1 if isinstance(first_ds_field_value, list) else 1
    )
    logger.debug("handling dcpr request datasets custodian field")
    change_dataset_custodian_value(num_datasets, flat_data_dict)
    logger.debug(f"{num_datasets=}")
    data_dict = {}
    datasets: typing.List[typing.Dict] = [{} for i in range(num_datasets)]
    for name, value in flat_data_dict.items():
        if name in dataset_fields:
            logger.debug(f"Processing {name=} {value=}...")
            if num_datasets == 1:
                datasets[0][name] = value
            else:
                for ds_index, ds_value in enumerate(value):
                    logger.debug(f"Processing {ds_index=} {ds_value=}...")
                    datasets[ds_index][name] = ds_value
        else:
            data_dict[name] = value
    data_dict["datasets"] = datasets
    return data_dict


def change_dataset_custodian_value(datasets_num: int, ds: dict):
    """
    dataset custodian is submitted as E1,E2 form,
    accordingly we are changing to True/False values.
    """
    dataset_custodian = ds.get("dataset_custodian")  # legacy data don't have this
    if dataset_custodian is not None:
        if datasets_num == 1:
            if dataset_custodian == "E1":
                ds["dataset_custodian"] = True
            elif dataset_custodian == "E2":
                ds["dataset_custodian"] = False
        else:
            for idx in range(datasets_num):
                if dataset_custodian[idx] == "E1":
                    ds["dataset_custodian"][idx] = True
                elif dataset_custodian[idx] == "E2":
                    ds["dataset_custodian"][idx] = False
