"""Asynchronous jobs for EMC-DCPR"""

import logging
import typing

from ckan import model
from ckan.plugins import toolkit

from . import email_notifications
from .constants import (
    DatasetManagementActivityType,
    DcprManagementActivityType,
    NSIF_ORG_NAME,
    CSI_ORG_NAME,
)

logger = logging.getLogger(__name__)


def test_job(*args, **kwargs):
    logger.debug(f"inside test_job - {args=} {kwargs=}")


def _get_org_recipients(
    org_name: str,
    jinja_env,
) -> typing.List:
    organization = toolkit.get_action("organization_show")(
        context={"ignore_auth": True},
        data_dict={
            "id": org_name,
            "include_users": True,
        },
    )
    recipients = []
    subject_template = jinja_env.get_template(
        "email_notifications/dcpr_request_workflow_change_subject.txt"
    )
    body_template = jinja_env.get_template(
        "email_notifications/dcpr_request_workflow_change_reviewer_body.txt"
    )
    for user in organization.get("users", []):
        user_obj = model.User.get(user["id"])
        if user.get("state") == "active":
            recipients.append((user_obj, subject_template, body_template))
    return recipients


def _get_owner_recipient(user_obj, jinja_env) -> typing.Tuple:
    subject_template = jinja_env.get_template(
        "email_notifications/dcpr_request_workflow_change_subject.txt"
    )
    body_template = jinja_env.get_template(
        "email_notifications/dcpr_request_workflow_change_owner_body.txt"
    )
    return user_obj, subject_template, body_template


def notify_dcpr_actors_of_relevant_status_change(activity_id: str):
    activity = toolkit.get_action("activity_show")(
        context={
            "ignore_auth": True,
            "user": None,  # CKAN expects there to be a user in context but does not actually use it
        },
        data_dict={"id": activity_id, "include_data": True},
    )
    activity_type = DcprManagementActivityType(activity["type"])
    dcpr_request = activity.get("data", {}).get("dcpr_request")
    if dcpr_request is not None:
        owner_user = toolkit.get_action("user_show")(
            context={"ignore_auth": True}, data_dict={"id": dcpr_request.owner_user}
        )
        jinja_env = email_notifications.get_jinja_env()
        recipients = []
        if activity_type == DcprManagementActivityType.SUBMIT_DCPR_REQUEST:
            # notify NSIF members
            recipients.extend(_get_org_recipients(NSIF_ORG_NAME, jinja_env))
        elif activity_type == DcprManagementActivityType.ACCEPT_DCPR_REQUEST_NSIF:
            # notify owner and CSI members
            recipients.extend(_get_org_recipients(CSI_ORG_NAME, jinja_env))
            recipients.append(_get_owner_recipient(owner_user, jinja_env))
        elif activity_type == DcprManagementActivityType.REJECT_DCPR_REQUEST_NSIF:
            # notify owner
            recipients.append(_get_owner_recipient(owner_user, jinja_env))
        elif (
            activity_type
            == DcprManagementActivityType.REQUEST_CLARIFICATION_DCPR_REQUEST_NSIF
        ):
            # notify owner
            recipients.append(_get_owner_recipient(owner_user, jinja_env))
        elif (
            activity_type
            == DcprManagementActivityType.RESIGN_NSIF_REVIEWER_DCPR_REQUEST
        ):
            # notify NSIF members
            recipients.extend(_get_org_recipients(NSIF_ORG_NAME, jinja_env))
        elif activity_type == DcprManagementActivityType.ACCEPT_DCPR_REQUEST_CSI:
            # notify owner
            recipients.append(_get_owner_recipient(owner_user, jinja_env))
        elif activity_type == DcprManagementActivityType.REJECT_DCPR_REQUEST_CSI:
            # notify owner
            recipients.append(_get_owner_recipient(owner_user, jinja_env))
        elif (
            activity_type
            == DcprManagementActivityType.REQUEST_CLARIFICATION_DCPR_REQUEST_CSI
        ):
            # notify owner
            recipients.append(_get_owner_recipient(owner_user, jinja_env))
        elif (
            activity_type == DcprManagementActivityType.RESIGN_CSI_REVIEWER_DCPR_REQUEST
        ):
            # notify CSI members
            recipients.extend(_get_org_recipients(CSI_ORG_NAME, jinja_env))
        else:
            raise NotImplementedError

        for user_obj, subject_template, body_template in recipients:
            logger.debug(f"About to send a notification to {user_obj.name!r}...")
            subject = subject_template.render(
                site_title=toolkit.config.get("site_title", "SASDI EMC")
            )
            body = body_template.render(
                user_obj=user_obj,
                dcpr_request=dcpr_request,
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


def notify_org_admins_of_dataset_management_request(activity_id: str):
    activity = toolkit.get_action("activity_show")(
        context={
            "ignore_auth": True,
            "user": None,  # CKAN expects there to be a user in context but does not actually use it
        },
        data_dict={"id": activity_id, "include_data": True},
    )
    activity_type = DatasetManagementActivityType(activity["type"])
    dataset = activity.get("data", {}).get("package")
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
                logger.debug(f"About to send a notification to {user_obj.name!r}...")
                subject = subject_template.render(
                    site_title=toolkit.config.get("site_title", "SASDI EMC")
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
