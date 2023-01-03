"""Reimplementation of the core CKAN email notifications

This module reimplements the core CKAN email notifications in order to:

- be able to provide more visibility onto what is going on. This includes returning the
  number of emails being sent

- modify the default implementation in order to not require an active request

"""

import datetime as dt
import logging
import re

from ckan import (
    logic,
    model,
)
from ckan.plugins import toolkit

from ckanext.dalrrd_emc_dcpr.cli.utils import get_jinja_env

logger = logging.getLogger(__name__)


def get_and_send_notifications_for_all_users() -> int:
    context = {
        "model": model,
        "session": model.Session,
        "ignore_auth": True,
        "keep_email": True,
    }
    users = logic.get_action("user_list")(context, {})
    num_sent = 0
    for user in users:
        num_sent += get_and_send_notifications_for_user(user)
    return num_sent


def get_and_send_notifications_for_user(user) -> int:

    # Parse the email_notifications_since config setting, email notifications
    # from longer ago than this time will not be sent.
    email_notifications_since = toolkit.config.get(
        "ckan.email_notifications_since", "2 days"
    )
    email_notifications_since = string_to_timedelta(email_notifications_since)
    email_notifications_since = dt.datetime.utcnow() - email_notifications_since

    # FIXME: We are accessing model from lib here but I'm not sure what
    # else to do unless we add a get_email_last_sent() logic function which
    # would only be needed by this lib.
    email_last_sent = model.Dashboard.get(user["id"]).email_last_sent
    activity_stream_last_viewed = model.Dashboard.get(
        user["id"]
    ).activity_stream_last_viewed  # the dashboard database table only has userid, activity_stream_last_viewed, email_last_sent

    since = max(
        email_notifications_since, email_last_sent, activity_stream_last_viewed
    )  # the youngest

    notifications = get_notifications(user, since)
    num_sent = 0
    # TODO: Handle failures from send_email_notification.
    for notification in notifications:
        send_notification(user, notification)
        num_sent += 1

    # FIXME: We are accessing model from lib here but I'm not sure what
    # else to do unless we add a update_email_last_sent()
    # logic function which would only be needed by this lib.
    dash = model.Dashboard.get(user["id"])
    dash.email_last_sent = dt.datetime.utcnow()
    model.repo.commit()
    return num_sent


def send_notification(user, email_dict):
    """Email `email_dict` to `user`."""
    import ckan.lib.mailer

    if not user.get("email"):
        logger.debug(
            f"User {user.get('name')!r} does not have an email address configured"
        )
        # FIXME: Raise an exception.
        return

    try:
        ckan.lib.mailer.mail_recipient(
            user["display_name"],
            user["email"],
            email_dict["subject"],
            email_dict["body"],
        )
    except ckan.lib.mailer.MailerException:
        raise
    else:
        logger.debug(f"Email sent!")


def _notifications_for_activities(activities, user_dict):
    """Return one or more email notifications covering the given activities.

    This function handles grouping multiple activities into a single digest
    email.

    :param activities: the activities to consider
    :type activities: list of activity dicts like those returned by
        ckan.logic.action.get.dashboard_activity_list()

    :returns: a list of email notifications
    :rtype: list of dicts each with keys 'subject' and 'body'

    """
    if not activities:
        return []

    if not user_dict.get("activity_streams_email_notifications"):
        return []

    # We just group all activities into a single "new activity" email that
    # doesn't say anything about _what_ new activities they are.
    # TODO: Here we could generate some smarter content for the emails e.g.
    # say something about the contents of the activities, or single out
    # certain types of activity to be sent in their own individual emails,
    # etc.
    subject = toolkit.ungettext(
        "{n} new activity from {site_title}",
        "{n} new activities from {site_title}",
        len(activities),
    ).format(site_title=toolkit.config.get("ckan.site_title"), n=len(activities))
    jinja_env = get_jinja_env()
    body_template = jinja_env.get_template("email_notifications/email_body.txt")
    rendered_body = body_template.render(
        activities=activities,
        site_url=toolkit.config.get("ckan.site_url"),
        site_title=toolkit.config.get("ckan.site_title"),
    )
    notifications = [{"subject": subject, "body": rendered_body}]

    return notifications


def _notifications_from_dashboard_activity_list(user_dict, since):
    """Return any email notifications from the given user's dashboard activity
    list since `since`.

    """
    # Get the user's dashboard activity stream.
    context = {"model": model, "session": model.Session, "user": user_dict["id"]}
    activities = logic.get_action("dashboard_activity_list")(context, {})

    # Filter out the user's own activities., so they don't get an email every
    # time they themselves do something (we are not Trac).
    activities = [act for act in activities if act["user_id"] != user_dict["id"]]

    # Filter out the old activities.
    strptime = dt.datetime.strptime
    fmt = "%Y-%m-%dT%H:%M:%S.%f"
    activities = [act for act in activities if strptime(act["timestamp"], fmt) > since]
    return _notifications_for_activities(activities, user_dict)


# A list of functions that provide email notifications for users from different
# sources. Add to this list if you want to implement a new source of email
# notifications.
_notifications_functions = [
    _notifications_from_dashboard_activity_list,
]


def get_notifications(user_dict, since):
    """Return any email notifications for the given user since `since`.

    For example email notifications about activity streams will be returned for
    any activities the occurred since `since`.

    :param user_dict: a dictionary representing the user, should contain 'id'
        and 'name'
    :type user_dict: dictionary

    :param since: datetime after which to return notifications from
    :rtype since: datetime.datetime

    :returns: a list of email notifications
    :rtype: list of dicts with keys 'subject' and 'body'

    """
    notifications = []
    logger.debug(f"Retrieving notifications for {user_dict['name']!r} since {since!r}")
    for function in _notifications_functions:
        notifications.extend(function(user_dict, since))
    return notifications


def string_to_timedelta(s):
    """Parse a string s and return a standard datetime.timedelta object.

    Handles days, hours, minutes, seconds, and microseconds.

    Accepts strings in these formats:

    2 days
    14 days
    4:35:00 (hours, minutes and seconds)
    4:35:12.087465 (hours, minutes, seconds and microseconds)
    7 days, 3:23:34
    7 days, 3:23:34.087465
    .087465 (microseconds only)

    :raises ckan.logic.ValidationError: if the given string does not match any
        of the recognised formats

    """
    patterns = []
    days_only_pattern = "(?P<days>\d+)\s+day(s)?"
    patterns.append(days_only_pattern)
    hms_only_pattern = "(?P<hours>\d?\d):(?P<minutes>\d\d):(?P<seconds>\d\d)"
    patterns.append(hms_only_pattern)
    ms_only_pattern = ".(?P<milliseconds>\d\d\d)(?P<microseconds>\d\d\d)"
    patterns.append(ms_only_pattern)
    hms_and_ms_pattern = hms_only_pattern + ms_only_pattern
    patterns.append(hms_and_ms_pattern)
    days_and_hms_pattern = "{0},\s+{1}".format(days_only_pattern, hms_only_pattern)
    patterns.append(days_and_hms_pattern)
    days_and_hms_and_ms_pattern = days_and_hms_pattern + ms_only_pattern
    patterns.append(days_and_hms_and_ms_pattern)

    for pattern in patterns:
        match = re.match("^{0}$".format(pattern), s)
        if match:
            break

    if not match:
        raise logic.ValidationError("Not a valid time: {0}".format(s))

    gd = match.groupdict()
    days = int(gd.get("days", "0"))
    hours = int(gd.get("hours", "0"))
    minutes = int(gd.get("minutes", "0"))
    seconds = int(gd.get("seconds", "0"))
    milliseconds = int(gd.get("milliseconds", "0"))
    microseconds = int(gd.get("microseconds", "0"))
    delta = dt.timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds,
        microseconds=microseconds,
    )
    return delta
