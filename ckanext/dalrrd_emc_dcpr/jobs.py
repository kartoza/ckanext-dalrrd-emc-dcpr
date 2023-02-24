"""Asynchronous jobs for EMC-DCPR"""

import logging
import typing

from ckan import model
from ckan.plugins import toolkit

from . import (
    email_notifications,
    provide_request_context,
)
from .constants import (
    DatasetManagementActivityType,
    DcprManagementActivityType,
    NSIF_ORG_NAME,
    CSI_ORG_NAME,
)

logger = logging.getLogger(__name__)


def test_job(*args, **kwargs):
    logger.debug(f"inside test_job - {args=} {kwargs=}")


@provide_request_context
def notify_dcpr_actors_of_relevant_status_change(context, activity_id: str):
    activity_obj = model.Activity.get(activity_id)
    if activity_obj is not None:
        activity_type = DcprManagementActivityType(activity_obj.activity_type)
        dcpr_request = (activity_obj.data or {}).get("dcpr_request")
        if dcpr_request is not None:
            owner_user_obj = model.User.get(dcpr_request["owner_user"])
            nsif_reviewer_obj = model.User.get(dcpr_request["nsif_reviewer"])
            csi_reviewer_obj = model.User.get(dcpr_request["csi_moderator"])
            render_context = {
                "site_title": toolkit.config.get("ckan.site_title", "SASDI EMC"),
                "site_url": toolkit.config.get("ckan.site_url"),
                "admin_team_email": toolkit.config.get("email_to"),
                "dcpr_request": dcpr_request,
                "dcpr_request_detail_url": toolkit.h.url_for(
                    "dcpr.dcpr_request_show",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                ),
                "dcpr_request_edit_url": toolkit.h.url_for(
                    "dcpr.owner_edit_dcpr_request",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                ),
                "become_nsif_reviewer_url": toolkit.url_for(
                    "dcpr.dcpr_request_become_reviewer",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                    organization=NSIF_ORG_NAME,
                ),
                "confirm_nsif_reviewer_role_url": toolkit.h.url_for(
                    "dcpr.dcpr_request_become_reviewer",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                    organization=NSIF_ORG_NAME,
                ),
                "become_csi_reviewer_url": toolkit.url_for(
                    "dcpr.dcpr_request_become_reviewer",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                    organization=CSI_ORG_NAME,
                ),
                "confirm_csi_reviewer_role_url": toolkit.h.url_for(
                    "dcpr.dcpr_request_become_reviewer",
                    csi_reference_id=dcpr_request["csi_reference_id"],
                    organization=CSI_ORG_NAME,
                ),
                "activity_type": activity_type,
                "owner_user_obj": owner_user_obj,
                "nsif_reviewer_obj": nsif_reviewer_obj,
                "csi_reviewer_obj": csi_reviewer_obj,
            }
            if (
                activity_type == DcprManagementActivityType.SUBMIT_DCPR_REQUEST
            ):  # notify NSIF members
                render_context.update(
                    {
                        "current_org": NSIF_ORG_NAME,
                        "action_subject_message": toolkit._(
                            "has been submitted for moderation"
                        ),
                    }
                )
                messages = _get_dcpr_nsif_rendered_messages(render_context)
            elif (
                activity_type == DcprManagementActivityType.ACCEPT_DCPR_REQUEST_NSIF
            ):  # notify owner and CSI members
                render_context.update(
                    {
                        "current_org": CSI_ORG_NAME,
                        "action_subject_message": toolkit._(
                            "has been accepted by NSIF"
                        ),
                    }
                )
                messages = _get_dcpr_csi_rendered_messages(render_context)
                messages.extend(
                    _get_dcpr_owner_rendered_messages([owner_user_obj], render_context)
                )
            elif (
                activity_type == DcprManagementActivityType.REJECT_DCPR_REQUEST_NSIF
            ):  # notify owner
                render_context["action_subject_message"] = toolkit._(
                    "has been rejected by NSIF"
                )
                messages = _get_dcpr_owner_rendered_messages(
                    [owner_user_obj], render_context
                )
            elif (
                activity_type
                == DcprManagementActivityType.REQUEST_CLARIFICATION_DCPR_REQUEST_NSIF
            ):  # notify owner
                render_context["action_subject_message"] = toolkit._(
                    "needs clarification"
                )
                messages = _get_dcpr_owner_rendered_messages(
                    [owner_user_obj], render_context
                )
            elif (
                activity_type
                == DcprManagementActivityType.RESIGN_NSIF_REVIEWER_DCPR_REQUEST
            ):  # notify NSIF members
                render_context.update(
                    {
                        "current_org": NSIF_ORG_NAME,
                        "action_subject_message": toolkit._(
                            "has had its NSIF reviewer step down"
                        ),
                    }
                )
                messages = _get_dcpr_nsif_rendered_messages(render_context)
            elif (
                activity_type == DcprManagementActivityType.ACCEPT_DCPR_REQUEST_CSI
            ):  # notify owner
                render_context["action_subject_message"] = toolkit._(
                    "has been accepted by CSI"
                )
                messages = _get_dcpr_owner_rendered_messages(
                    [owner_user_obj], render_context
                )
            elif (
                activity_type == DcprManagementActivityType.REJECT_DCPR_REQUEST_CSI
            ):  # notify owner
                render_context["action_subject_message"] = toolkit._(
                    "has been rejected by CSI"
                )
                messages = _get_dcpr_owner_rendered_messages(
                    [owner_user_obj], render_context
                )
            elif (
                activity_type
                == DcprManagementActivityType.REQUEST_CLARIFICATION_DCPR_REQUEST_CSI
            ):  # notify owner
                render_context["action_subject_message"] = toolkit._(
                    "needs clarification"
                )
                messages = _get_dcpr_owner_rendered_messages(
                    [owner_user_obj], render_context
                )
            elif (
                activity_type
                == DcprManagementActivityType.RESIGN_CSI_REVIEWER_DCPR_REQUEST
            ):  # notify CSI members
                render_context.update(
                    {
                        "current_org": CSI_ORG_NAME,
                        "action_subject_message": toolkit._(
                            "has had its CSI reviewer step down"
                        ),
                    }
                )
                messages = _get_dcpr_csi_rendered_messages(render_context)
            else:
                raise NotImplementedError
            for user_obj, subject, body in messages:
                logger.debug(f"{subject=}")
                logger.debug(f"{body=}")
                logger.debug(f"----------")
                email_notifications.send_notification(
                    {
                        "name": user_obj.name,
                        "display_name": user_obj.display_name,
                        "email": user_obj.email,
                    },
                    {"subject": subject, "body": body},
                )
    else:
        raise RuntimeError(f"Could not retrieve activity with id {activity_id!r}")


def notify_org_admins_of_dataset_management_request(activity_id: str):
    activity_obj = model.Activity.get(activity_id)
    if activity_obj is not None:
        activity_type = DatasetManagementActivityType(activity_obj.activity_type)
        dataset = (activity_obj.data or {}).get("package")
        templates_map = {
            DatasetManagementActivityType.REQUEST_PUBLICATION: (),
            DatasetManagementActivityType.REQUEST_MAINTENANCE: (
                "email_notifications/dataset_maintenance_request_subject.txt",
                "email_notifications/dataset_maintenance_request_body.txt",
            ),
        }
        if dataset is not None:
            org_id = dataset["owner_org"]
            organization = toolkit.get_action("organization_show")(
                context={"ignore_auth": True},
                data_dict={
                    "id": org_id,
                    "include_users": True,
                },
            )
            jinja_env = email_notifications.get_jinja_env()
            subject_path, body_path = templates_map[activity_type]
            subject_template = jinja_env.get_template(subject_path)
            body_template = jinja_env.get_template(body_path)
            for member in organization.get("users", []):
                is_active = member.get("state") == "active"
                is_org_admin = member.get("capacity") == "admin"
                if is_active and is_org_admin:
                    user_obj = model.User.get(member["id"])
                    logger.debug(
                        f"About to send a notification to {user_obj.name!r}..."
                    )
                    subject = subject_template.render(
                        site_title=toolkit.config.get("ckan.site_title", "SASDI EMC")
                    )
                    body = body_template.render(
                        organization=organization,
                        user_obj=user_obj,
                        dataset=dataset,
                        h=toolkit.h,
                        site_url=toolkit.config.get("ckan.site_url", ""),
                    )
                    email_notifications.send_notification(
                        {
                            "name": user_obj.name,
                            "display_name": user_obj.display_name,
                            "email": user_obj.email,
                        },
                        {"subject": subject, "body": body},
                    )
    else:
        raise RuntimeError(f"Could not retrieve activity with id {activity_id!r}")


def _get_dcpr_owner_rendered_messages(
    owners: typing.List[model.User],
    render_context: typing.Dict,
) -> typing.List[typing.Tuple[model.User, str, str]]:
    return _get_dcpr_rendered_messages(
        owners,
        render_context=render_context,
        subject_template_path="email_notifications/dcpr_request_workflow_change_subject.txt",
        body_template_path="email_notifications/dcpr_request_workflow_change_owner_body.txt",
    )


def _get_dcpr_nsif_rendered_messages(
    render_context: typing.Dict,
) -> typing.List[typing.Tuple[model.User, str, str]]:
    return _get_dcpr_rendered_messages(
        _get_org_members(NSIF_ORG_NAME),
        render_context=render_context,
        subject_template_path="email_notifications/dcpr_request_workflow_change_subject.txt",
        body_template_path="email_notifications/dcpr_request_workflow_change_reviewer_body.txt",
    )


def _get_dcpr_csi_rendered_messages(
    render_context: typing.Dict,
) -> typing.List[typing.Tuple[model.User, str, str]]:
    return _get_dcpr_rendered_messages(
        _get_org_members(CSI_ORG_NAME),
        render_context=render_context,
        subject_template_path="email_notifications/dcpr_request_workflow_change_subject.txt",
        body_template_path="email_notifications/dcpr_request_workflow_change_reviewer_body.txt",
    )


def _get_dcpr_rendered_messages(
    recipients: typing.List,
    render_context: typing.Dict,
    subject_template_path: str,
    body_template_path: str,
) -> typing.List[typing.Tuple[model.User, str, str]]:
    logger.debug("render context:", render_context, "\n", "recipients:", recipients)
    jinja_env = email_notifications.get_jinja_env()
    subject_template = jinja_env.get_template(subject_template_path)
    body_template = jinja_env.get_template(body_template_path)
    result = []
    for user_obj in recipients:
        subject_context = render_context.copy()
        subject_context["recipient_user_obj"] = user_obj
        body_context = render_context.copy()
        body_context["recipient_user_obj"] = user_obj
        rendered_subject = subject_template.render(**subject_context)
        rendered_body = body_template.render(**body_context)
        result.append((user_obj, rendered_subject, rendered_body))
    return result


def _get_org_members(org_name: str) -> typing.List:
    organization: typing.Dict = toolkit.get_action("organization_show")(
        context={"ignore_auth": True},
        data_dict={
            "id": org_name,
            "include_users": True,
        },
    )
    members = []
    for user in organization.get("users", []):
        user_obj = model.User.get(user["id"])
        if user.get("state") == "active":
            members.append(user_obj)
    return members
