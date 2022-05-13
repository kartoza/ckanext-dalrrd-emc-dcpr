import json
import logging
import typing

import ckan.lib.navl.dictization_functions as dict_fns
import ckan.model
from flask import Blueprint, redirect, request
from flask.views import MethodView
from ckan.views.home import CACHE_PARAMETERS
from ckan.plugins import toolkit
from ckan.logic import clean_dict, parse_params, tuplize_dict
from ckan.views import dataset as ckan_dataset_views

from ..helpers import get_status_labels
from ..model.dcpr_request import DCPRRequestOrganizationLevel, DCPRRequestUrgency
from ..model import dcpr_request as dcpr_request_model
from ..constants import DCPRRequestStatus

logger = logging.getLogger(__name__)

dcpr_blueprint = Blueprint(
    "dcpr", __name__, template_folder="templates", url_prefix="/dcpr"
)


@dcpr_blueprint.route("/")
def get_public_dcpr_requests():
    logger.debug("Inside the dcpr_home view")
    existing_public_requests = toolkit.get_action("dcpr_request_list_public")(
        data_dict={}
    )
    extra_vars = {
        "dcpr_requests": existing_public_requests,
        "statuses": get_status_labels(),
    }
    return toolkit.render("dcpr/list.html", extra_vars=extra_vars)


@dcpr_blueprint.route("/my-dcpr-requests")
def get_my_dcpr_requests():
    dcpr_requests = toolkit.get_action("my_dcpr_request_list")(
        context={"user": toolkit.g.user}
    )
    extra_vars = {
        "dcpr_requests": dcpr_requests,
        "statuses": get_status_labels(),
    }
    return toolkit.render("dcpr/list.html", extra_vars=extra_vars)


@dcpr_blueprint.route("/awaiting-csi-moderation-dcpr-requests")
def get_awaiting_csi_moderation_dcpr_requests():
    raise NotImplementedError


@dcpr_blueprint.route("/awaiting-nsif-moderation-dcpr-requests")
def get_awaiting_nsif_moderation_dcpr_requests():
    try:
        dcpr_requests = toolkit.get_action(
            "dcpr_request_list_awaiting_nsif_moderation"
        )(
            context={"user": toolkit.g.user},
        )
    except toolkit.NotAuthorized:
        result = toolkit.abort(
            403,
            toolkit._(
                "You are not authorized to list DCPR requests awaiting NSIF moderation"
            ),
        )
    else:
        result = toolkit.render(
            "dcpr/list.html",
            extra_vars={
                "dcpr_requests": dcpr_requests,
                "statuses": get_status_labels(),
            },
        )
    return result


class DcprRequestCreateView(MethodView):
    def get(self, data=None, errors=None, error_summary=None):
        toolkit.check_access("dcpr_request_create_auth", {"user": toolkit.g.user})
        data_to_show = data or clean_dict(
            dict_fns.unflatten(
                tuplize_dict(parse_params(request.args, ignore_keys=CACHE_PARAMETERS))
            )
        )
        serialized_errors = json.dumps(errors or {})
        serialized_error_summary = json.dumps(error_summary or {})
        logger.info(f"{data_to_show=}")
        logger.info(f"{serialized_errors=}")
        logger.info(f"{serialized_error_summary=}")
        extra_vars = {
            "form_snippet": "dcpr/snippets/request_form.html",
            "csi_reference_id": None,
            "data": data_to_show,
            "errors": errors or {},
            "error_summary": error_summary or {},
            "data_urgency": [
                {"value": level.value, "text": level.value}
                for level in DCPRRequestUrgency
            ],
            # TODO: perhaps we can provide the name of the form that will be shown, as it will presumably be different according with the user role
        }
        return toolkit.render("dcpr/edit.html", extra_vars=extra_vars)

    def post(self):
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
        except dict_fns.DataError:
            result = toolkit.abort(400, toolkit._("Integrity Error"))
        else:
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
                # result = dcpr_request_edit(
                #     None, data=data_dict, errors=errors, error_summary=error_summary
                # )
            else:
                url = toolkit.h.url_for(
                    "dcpr.dcpr_request_show",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                )
                result = toolkit.h.redirect_to(url)
        return result


new_dcpr_request_view = DcprRequestCreateView.as_view("new_dcpr_request")
dcpr_blueprint.add_url_rule("/request/new/", view_func=new_dcpr_request_view)


class DcprRequestOwnerUpdateView(MethodView):
    def get(
        self,
        csi_reference_id: str,
        data: typing.Optional[typing.Dict] = None,
        errors: typing.Optional[typing.Dict] = None,
        error_summary=None,
    ):
        context = _prepare_context()
        try:
            old_data = toolkit.get_action("dcpr_request_show")(
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
                    "dcpr_request_update_by_owner_auth",
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
                    "dcpr/edit.html",
                    extra_vars={
                        "form_snippet": "dcpr/snippets/request_form.html",
                        "data": data,
                        "csi_reference_id": csi_reference_id,
                        "errors": errors or {},
                        "error_summary": error_summary or {},
                        "data_urgency": [
                            {"value": level.value, "text": level.value}
                            for level in DCPRRequestUrgency
                        ],
                    },
                )
        return result


owner_edit_dcpr_request_view = DcprRequestOwnerUpdateView.as_view(
    "owner_edit_dcpr_request"
)
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/owner_edit/", view_func=owner_edit_dcpr_request_view
)


class DcprRequestNsifUpdateView(MethodView):
    def get(
        self,
        csi_reference_id: str,
        data: typing.Optional[typing.Dict] = None,
        errors: typing.Optional[typing.Dict] = None,
        error_summary=None,
    ):
        raise NotImplementedError


nsif_edit_dcpr_request_view = DcprRequestNsifUpdateView.as_view(
    "nsif_edit_dcpr_request"
)
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/nsif_edit/", view_func=nsif_edit_dcpr_request_view
)


@dcpr_blueprint.route("/request/<csi_reference_id>")
def dcpr_request_show(csi_reference_id):
    try:
        dcpr_request = toolkit.get_action("dcpr_request_show")(
            context={}, data_dict={"csi_reference_id": csi_reference_id}
        )
    except toolkit.ObjectNotFound:
        result = toolkit.abort(404, toolkit._("DCPR request not found"))
    except toolkit.NotAuthorized:
        result = toolkit.base.abort(401, toolkit._("Not authorized"))
    else:

        is_nsif_reviewer = toolkit.h["emc_user_is_org_member"](
            "nsif", toolkit.g.userobj
        )
        is_csi_reviewer = toolkit.h["emc_user_is_org_member"]("csi", toolkit.g.userobj)

        extra_vars = {
            "dcpr_request": dcpr_request,
            "is_owner": dcpr_request["owner_user"] == toolkit.g.userobj.id,
            "is_nsif_reviewer": is_nsif_reviewer,
            "is_csi_reviewer": is_csi_reviewer,
        }
        result = toolkit.render("dcpr/show.html", extra_vars=extra_vars)
    return result


#     extra_vars["request_status"] = get_status_labels()
#
#     nsif_reviewer = toolkit.h["emc_user_is_org_member"](
#         "nsif", toolkit.g.userobj, role="editor"
#     )
#     csi_reviewer = toolkit.h["emc_user_is_org_member"](
#         "csi", toolkit.g.userobj, role="editor"
#     )
#
#     extra_vars["nsif_reviewer"] = nsif_reviewer
#     extra_vars["csi_reviewer"] = csi_reviewer
#
#     try:
#         dcpr_request = toolkit.get_action("dcpr_request_show")(data_dict=data_dict)
#         request_owner = (
#             dcpr_request["owner_user"] == toolkit.g.userobj.id
#             if toolkit.g.userobj
#             else False
#         )
#
#         extra_vars["dcpr_request"] = dcpr_request
#         extra_vars["request_owner"] = request_owner
#
#     except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
#         return toolkit.base.abort(404, toolkit._("Request not found"))
#
#     return toolkit.render("dcpr/show.html", extra_vars=extra_vars)
#
#
# @dcpr_blueprint.route("/request/update/<request_id>", methods=["POST"])
# def dcpr_request_update(request_id, data=None, errors=None, error_summary=None):
#     logger.debug("Inside the dcpr_request_edit view")
#     extra_vars = {}
#     extra_vars["errors"] = errors
#
#     context = {
#         "user": toolkit.g.user,
#         "auth_user_obj": toolkit.g.userobj,
#     }
#
#     try:
#         data_dict = clean_dict(
#             dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
#         )
#         data_dict["csi_moderator"] = None
#         data_dict["nsif_reviewer"] = None
#         data_dict["id"] = request_id
#
#     except dict_fns.DataError:
#         return toolkit.base.abort(400, toolkit._("Integrity Error"))
#     try:
#         toolkit.get_action("dcpr_request_update")(context, data_dict)
#
#         url = toolkit.h.url_for(
#             "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#         )
#         return toolkit.h.redirect_to(url)
#
#     except toolkit.NotAuthorized as e:
#         return toolkit.base.abort(
#             403,
#             toolkit._("Unauthorized to perfom the action, %s") % e,
#         )
#     except toolkit.ObjectNotFound as e:
#         return toolkit.base.abort(404, toolkit._("DCPR request not found"))
#     except toolkit.ValidationError as e:
#         errors = e.error_dict
#         error_summary = e.error_summary
#
#         request.method = "GET"
#         return dcpr_request_edit(
#             data_dict.get("request_id", None), data_dict, errors, error_summary
#         )
#
#     url = toolkit.h.url_for(
#         "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#     )
#     return toolkit.h.redirect_to(url)
#
#
# FIXME - deprecate this in favor of the DcprRequestSubmitView
def dcpr_request_submit(csi_reference_id):
    context = {
        "user": toolkit.g.user,
        "auth_user_obj": toolkit.g.userobj,
    }

    try:
        toolkit.get_action("dcpr_request_submit")(
            context, data_dict={"csi_reference_id": csi_reference_id}
        )
    except toolkit.NotAuthorized as e:
        result = toolkit.base.abort(
            403,
            toolkit._("Unauthorized to perfom the action, %s") % e,
        )
    except toolkit.ObjectNotFound:
        result = toolkit.base.abort(404, toolkit._("DCPR request not found"))
    else:
        result = toolkit.h.redirect_to(
            toolkit.h.url_for(
                "dcpr.dcpr_request_show", csi_reference_id=csi_reference_id
            )
        )
    return result


class DcprRequestSubmitView(MethodView):
    def get(self, csi_reference_id: str):
        # show a template for the user to confirm submission
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            return toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            return toolkit.abort(403, toolkit._("Unauthorized to submit DCPR request"))
        return toolkit.render(
            "dcpr/ask_for_confirmation.html",
            extra_vars={
                "dcpr_request": dcpr_request,
                "action": "submit",
                "action_url": toolkit.h["url_for"](
                    "dcpr.dcpr_request_submit", csi_reference_id=csi_reference_id
                ),
            },
        )

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


class DcprRequestClaimView(MethodView):
    def get(self, csi_reference_id: str, organization: str):
        context = _prepare_context()
        try:
            dcpr_request = toolkit.get_action("dcpr_request_show")(
                context, data_dict={"csi_reference_id": csi_reference_id}
            )
        except toolkit.ObjectNotFound:
            return toolkit.abort(404, toolkit._("DCPR request not found"))
        except toolkit.NotAuthorized:
            return toolkit.abort(403, toolkit._("Unauthorized to claim DCPR request"))
        action = {
            "nsif": "become NSIF reviewer",
            "csi": "become CSI reviewer",
        }.get(organization)
        return toolkit.render(
            "dcpr/ask_for_confirmation.html",
            extra_vars={
                "dcpr_request": dcpr_request,
                "action": action,
                "action_url": toolkit.h["url_for"](
                    "dcpr.dcpr_request_claim_reviewer",
                    csi_reference_id=csi_reference_id,
                    organization=organization,
                ),
            },
        )

    def post(self, csi_reference_id: str, organization: str):
        if "cancel" not in request.form.keys():
            context = _prepare_context()
            action_name = {
                "nsif": "claim_dcpr_request_nsif_reviewer",
                "csi": "claim_dcpr_request_csi_moderator",
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
                toolkit.h["flash_notice"](toolkit._("DCPR request has been claimed."))
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


claim_dcpr_request_view = DcprRequestClaimView.as_view("dcpr_request_claim_reviewer")
dcpr_blueprint.add_url_rule(
    "/request/<csi_reference_id>/claim/<organization>",
    view_func=claim_dcpr_request_view,
)


# @dcpr_blueprint.route("/request/escalate/<request_id>", methods=["POST"])
# def dcpr_request_escalate(request_id, data=None, errors=None, error_summary=None):
#     logger.debug("Inside the dcpr_request_edit view")
#     data_dict = {"id": request_id}
#     extra_vars = {}
#     extra_vars["errors"] = errors
#
#     context = {
#         "user": toolkit.g.user,
#         "auth_user_obj": toolkit.g.userobj,
#     }
#
#     try:
#         data_dict = clean_dict(
#             dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
#         )
#         data_dict["csi_moderator"] = None
#
#     except dict_fns.DataError:
#         return toolkit.base.abort(400, toolkit._("Integrity Error"))
#     try:
#         toolkit.get_action("dcpr_request_escalate")(context, data_dict)
#
#         url = toolkit.h.url_for(
#             "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#         )
#         return toolkit.h.redirect_to(url)
#
#     except toolkit.NotAuthorized as e:
#         return toolkit.base.abort(
#             403,
#             toolkit._("Unauthorized to perfom the action, %s") % e,
#         )
#     except toolkit.ObjectNotFound as e:
#         return toolkit.base.abort(404, toolkit._("DCPR request not found"))
#     except toolkit.ValidationError as e:
#         errors = e.error_dict
#         error_summary = e.error_summary
#
#         request.method = "GET"
#         return dcpr_request_edit(
#             data_dict.get("request_id", None), data_dict, errors, error_summary
#         )
#
#     url = toolkit.h.url_for(
#         "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#     )
#     return toolkit.h.redirect_to(url)
#
#
# @dcpr_blueprint.route("/request/accept/<request_id>", methods=["POST"])
# def dcpr_request_accept(request_id, data=None, errors=None, error_summary=None):
#     logger.debug("Inside the dcpr_request_accept view")
#     data_dict = {"id": request_id}
#     extra_vars = {}
#     extra_vars["errors"] = errors
#
#     context = {
#         "user": toolkit.g.user,
#         "auth_user_obj": toolkit.g.userobj,
#     }
#
#     try:
#         data_dict = clean_dict(
#             dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
#         )
#
#     except dict_fns.DataError:
#         return toolkit.base.abort(400, toolkit._("Integrity Error"))
#     try:
#         toolkit.get_action("dcpr_request_accept")(context, data_dict)
#
#         url = toolkit.h.url_for(
#             "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#         )
#         return toolkit.h.redirect_to(url)
#
#     except toolkit.NotAuthorized as e:
#         return toolkit.base.abort(
#             403,
#             toolkit._("Unauthorized to perfom the action, %s") % e,
#         )
#     except toolkit.ObjectNotFound as e:
#         return toolkit.base.abort(404, toolkit._("DCPR request not found"))
#     except toolkit.ValidationError as e:
#         errors = e.error_dict
#         error_summary = e.error_summary
#
#         request.method = "GET"
#         return dcpr_request_edit(
#             data_dict.get("request_id", None), data_dict, errors, error_summary
#         )
#
#     url = toolkit.h.url_for(
#         "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#     )
#     return toolkit.h.redirect_to(url)
#
#
# @dcpr_blueprint.route("/request/reject/<request_id>", methods=["POST"])
# def dcpr_request_reject(request_id, data=None, errors=None, error_summary=None):
#     logger.debug("Inside the dcpr_request_reject view")
#     data_dict = {"id": request_id}
#     extra_vars = {}
#     extra_vars["errors"] = errors
#
#     context = {
#         "user": toolkit.g.user,
#         "auth_user_obj": toolkit.g.userobj,
#     }
#
#     try:
#         data_dict = clean_dict(
#             dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
#         )
#
#     except dict_fns.DataError:
#         return toolkit.base.abort(400, toolkit._("Integrity Error"))
#     try:
#         toolkit.get_action("dcpr_request_reject")(context, data_dict)
#
#         url = toolkit.h.url_for(
#             "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#         )
#         return toolkit.h.redirect_to(url)
#
#     except toolkit.NotAuthorized as e:
#         return toolkit.base.abort(
#             403,
#             toolkit._("Unauthorized to perfom the action, %s") % e,
#         )
#     except toolkit.ObjectNotFound as e:
#         return toolkit.base.abort(404, toolkit._("DCPR request not found"))
#     except toolkit.ValidationError as e:
#         errors = e.error_dict
#         error_summary = e.error_summary
#
#         request.method = "GET"
#         return dcpr_request_edit(
#             data_dict.get("request_id", None), data_dict, errors, error_summary
#         )
#
#     url = toolkit.h.url_for(
#         "{0}.dcpr_request_show".format("dcpr"), request_id=request_id
#     )
#     return toolkit.h.redirect_to(url)


@dcpr_blueprint.route("/request/edit/<request_id>", methods=["GET"])
def dcpr_request_edit(request_id, data=None, errors=None, error_summary=None):
    logger.debug("Inside the dcpr_request_edit view")
    orgs = toolkit.get_action("organization_list")(data_dict={"all_fields": True})
    extra_vars = {
        "errors": errors,
        "organizations": [
            {"value": org["name"], "text": org["display_name"]} for org in orgs
        ],
        "organizations_levels": [
            {"value": level.value, "text": level.value}
            for level in DCPRRequestOrganizationLevel
        ],
        "data_urgency": [
            {"value": level.value, "text": level.value} for level in DCPRRequestUrgency
        ],
    }

    context = {"user": toolkit.g.user}

    try:
        data_dict = {"id": request_id}
        if request_id is not None:
            dcpr_request = toolkit.get_action("dcpr_request_show")(data_dict=data_dict)
            extra_vars["dcpr_request"] = dcpr_request
        elif data is not None:
            extra_vars["dcpr_request"] = data
            extra_vars["error_summary"] = error_summary

        nsif_reviewer = toolkit.h["emc_user_is_org_member"](
            "nsif", toolkit.g.userobj, role="editor"
        )
        csi_reviewer = toolkit.h["emc_user_is_org_member"](
            "csi", toolkit.g.userobj, role="editor"
        )
        extra_vars["nsif_reviewer"] = nsif_reviewer
        extra_vars["csi_reviewer"] = csi_reviewer

    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        return toolkit.base.abort(404, toolkit._("Request not found"))

    try:
        toolkit.check_access("dcpr_request_edit_auth", context, data_dict)

    except toolkit.NotAuthorized:
        return toolkit.base.abort(
            403,
            toolkit._("User %r not authorized to edit the requested DCPR request")
            % (toolkit.g.user),
        )

    return toolkit.render("dcpr/edit.html", extra_vars=extra_vars)


# @dcpr_blueprint.route("/request/delete/<request_id>", methods=["GET", "POST"])
# def dcpr_request_delete(request_id, errors=None, error_summary=None):
#     logger.debug("Inside the dcpr_request_delete view")
#     data_dict = {"request_id": request_id}
#     extra_vars = {}
#
#     context = {
#         "user": toolkit.g.user,
#         "auth_user_obj": toolkit.g.userobj,
#     }
#
#     if request.method == "GET":
#         try:
#             toolkit.check_access(
#                 "dcpr_request_delete_auth", context, {"request_id": request_id}
#             )
#         except toolkit.NotAuthorized:
#             return toolkit.base.abort(
#                 403,
#                 toolkit._("User %r not authorized to delete DCPR requests")
#                 % (toolkit.g.user),
#             )
#
#         return toolkit.render("dcpr/delete.html", extra_vars=extra_vars)
#
#     else:
#         try:
#             dcpr_request = toolkit.get_action("dcpr_request_delete")(context, data_dict)
#
#             url = toolkit.h.url_for("{0}.dcpr_home".format("dcpr"))
#             return toolkit.h.redirect_to(url)
#
#         except toolkit.NotAuthorized as e:
#             return toolkit.base.abort(
#                 403,
#                 toolkit._("Unauthorized to perfom the action, %s") % e,
#             )
#         except toolkit.ObjectNotFound as e:
#             return toolkit.base.abort(404, toolkit._("DCPR request not found"))
#         except toolkit.ValidationError as e:
#             errors = e.error_dict
#             error_summary = e.error_summary
#             return dcpr_request_edit(
#                 dcpr_request.csi_reference_id, errors, error_summary
#             )
#
#         url = toolkit.h.url_for("{0}.dcpr_home".format("dcpr"))
#         return toolkit.h.redirect_to(url)


def _prepare_context() -> typing.Dict:
    context = {
        "model": ckan.model,
        "session": ckan.model.Session,
        "user": toolkit.g.user,
        "auth_user_obj": toolkit.g.userobj,
    }
    return context
