"""Asynchronous jobs for EMC-DCPR"""

import logging

from ckan import model
from ckan.plugins import toolkit

from . import email_notifications

logger = logging.getLogger(__name__)


def test_job(*args, **kwargs):
    logger.debug(f"inside test_job - {args=} {kwargs=}")


def notify_org_admins_of_dataset_maintenance_request(activity_id: str):
    activity = toolkit.get_action("activity_show")(
        context={
            "ignore_auth": True,
            "user": None,  # CKAN expects there to be a user in context but does not actually use it
        },
        data_dict={"id": activity_id, "include_data": True},
    )
    dataset = activity.get("data", {}).get("package")
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
        subject_template = jinja_env.get_template(
            "email_notifications/dataset_maintenance_request_subject.txt"
        )
        body_template = jinja_env.get_template(
            "email_notifications/dataset_maintenance_request_body.txt"
        )
        for member in organization.get("users", []):
            logger.debug(f"{member=}")
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