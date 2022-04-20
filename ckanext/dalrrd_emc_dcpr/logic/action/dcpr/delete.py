import logging

from sqlalchemy import exc
from ckan.plugins import toolkit

from ....model import dcpr_request

logger = logging.getLogger(__name__)


def dcpr_request_delete(context, data_dict):
    logger.debug("Inside the dcpr_request_delete action")
    model = context["model"]
    toolkit.check_access("dcpr_request_delete_auth", context, data_dict)

    request_obj = model.Session.query(dcpr_request.DCPRRequest).get(
        data_dict["request_id"]
    )

    request_dataset_obj = model.Session.query(dcpr_request.DCPRRequestDataset).filter(
        dcpr_request.DCPRRequestDataset.dcpr_request_id == data_dict["request_id"]
    )

    notification_targets = model.Session.query(
        dcpr_request.DCPRRequestNotificationTarget
    ).filter(
        dcpr_request.DCPRRequestNotificationTarget.dcpr_request_id
        == data_dict["request_id"]
    )

    for target in notification_targets:
        target.delete()

    request_dataset_obj.delete()
    model.Session.delete(request_obj)

    try:
        model.Session.commit()
        model.repo.commit()

    except exc.InvalidRequestError as exception:
        model.Session.rollback()
    finally:
        model.Session.close()

    return request_obj
