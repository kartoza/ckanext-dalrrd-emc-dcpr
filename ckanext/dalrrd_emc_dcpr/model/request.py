import datetime

from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey

from ckan.model import core, domain_object, meta, types as _types, Session

from ckanext.dalrrd_emc_dcpr.model.request_dataset import (
    define_table as define_dataset_table,
    create_table as create_dataset_table,
)

__all__ = [
    "Request",
    "request_table",
    "request_notification_target_table",
    "request_nsif_reviewer_table",
    "request_csi_moderator_table",
]

request_table = None
request_csi_moderator_table = None
request_notification_target_table = None
request_nsif_reviewer_table = None
request_user_table = None


class Request(core.StatefulObjectMixin, domain_object.DomainObject):
    def __init__(self, **kw):
        super(Request, self).__init__(**kw)

    @classmethod
    def get(cls, reference, for_update=False):
        """
        Returns a request object referenced by its id or name.
        Implements same approach used in the ckan package model.
        """
        if not reference:
            return None

        q = meta.Session.query(cls)
        if for_update:
            q = q.with_for_update()
        request = q.get(reference)
        if request == None:
            request = cls.by_name(reference, for_update=for_update)
        return request


class RequestUser(domain_object.DomainObject):
    pass


class RequestCSIModerator(domain_object.DomainObject):
    pass


class RequestNotificationTarget(domain_object.DomainObject):
    pass


class RequestNSIFReview(domain_object.DomainObject):
    pass


def define_tables():

    global request_table
    global request_csi_moderator_table
    global request_notification_target_table
    global request_nsif_reviewer_table
    global request_user_table

    request_table = Table(
        "request",
        meta.metadata,
        Column(
            "csi_reference_id",
            types.UnicodeText,
            primary_key=True,
            default=_types.make_uuid,
        ),
        Column("status", types.UnicodeText),
        Column("organization_name", types.UnicodeText),
        Column("organization_level", types.UnicodeText),
        Column("organization_address", types.UnicodeText),
        Column("proposed_project_name", types.UnicodeText),
        Column("additional_project_context", types.UnicodeText),
        Column("capture_start_date", types.DateTime, default=datetime.datetime.utcnow),
        Column("capture_end_date", types.DateTime, default=datetime.datetime.utcnow),
        Column("cost", types.UnicodeText),
        Column("spatial_extent", types.UnicodeText),
        Column("spatial_resolution", types.UnicodeText),
        Column("data_capture_urgency", types.UnicodeText),
        Column("additional_information", types.UnicodeText),
        Column("additional_documents", types.UnicodeText),
        Column("request_date", types.DateTime, default=datetime.datetime.utcnow),
        Column("submission_date", types.DateTime, default=datetime.datetime.utcnow),
    )

    request_csi_moderator_table = Table(
        "request_csi_moderator",
        meta.metadata,
        Column("request_id", ForeignKey("request.csi_reference_id"), primary_key=True),
        Column("user_id", ForeignKey("user.id"), primary_key=True),
        Column("moderation_date", types.DateTime, default=datetime.datetime.utcnow),
        Column("moderator_notes", types.UnicodeText),
        Column("additional_documents", types.UnicodeText),
    )

    request_notification_target_table = Table(
        "notification_target",
        meta.metadata,
        Column(
            "target_id", types.UnicodeText, primary_key=True, default=_types.make_uuid
        ),
        Column("request_id", ForeignKey("request.csi_reference_id")),
        Column("user_id", ForeignKey("user.id")),
        Column("group_id", ForeignKey("group.id")),
    )

    request_nsif_reviewer_table = Table(
        "request_nsif_reviewer",
        meta.metadata,
        Column("request_id", ForeignKey("request.csi_reference_id"), primary_key=True),
        Column("user_id", ForeignKey("user.id"), primary_key=True),
        Column("review_date", types.DateTime, default=datetime.datetime.utcnow),
        Column("recommendation", types.Boolean, default=False),
        Column("review_notes", types.UnicodeText),
        Column("additional_documents", types.UnicodeText),
    )

    request_user_table = Table(
        "request_user",
        meta.metadata,
        Column("request_id", ForeignKey("request.csi_reference_id"), primary_key=True),
        Column("user_id", ForeignKey("user.id"), primary_key=True),
        Column("modified", types.DateTime, default=datetime.datetime.utcnow),
    )

    meta.mapper(Request, request_table)
    meta.mapper(RequestCSIModerator, request_csi_moderator_table)
    meta.mapper(RequestNotificationTarget, request_notification_target_table)
    meta.mapper(RequestNSIFReview, request_nsif_reviewer_table)
    meta.mapper(RequestUser, request_user_table)

    define_dataset_table()


def setup():

    if request_table is None:
        define_tables()
        log.debug("Request model tables have been defined")

    if not request_table.exists():
        try:
            request_table.create()
            request_csi_moderator_table.create()
            request_notification_target_table.create()
            request_nsif_reviewer_table.create()
            request_user_table.create()
            create_dataset_table()
        except Exception as e:
            if request_table.exists():
                Session.execute("DROP TABLE request")
                Session.commit()
            elif request_csi_moderator_table.exists():
                Session.execute("DROP TABLE request_csi_moderator")
                Session.commit()
            elif request_notification_target_table.exists():
                Session.execute("DROP TABLE request_notification_target")
                Session.commit()
            elif request_nsif_reviewer_table.exists():
                Session.execute("DROP TABLE request_nsif_reviewer")
                Session.commit()
            elif request_user_table.exists():
                Session.execute("DROP TABLE request_user")
                Session.commit()

            raise e

            log.debug("Request model tables has been created")
        else:
            log.debug("Problem in creating the Request model tables")
    else:
        log.debug("Request model tables already exists")
