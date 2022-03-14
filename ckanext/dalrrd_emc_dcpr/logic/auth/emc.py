import logging
import typing

logger = logging.getLogger(__name__)


def authorize_list_featured_datasets(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict]
) -> typing.Dict:
    return {"success": True}


def authorize_request_dataset_maintenance(
    context: typing.Dict, data_dict: typing.Dict
) -> typing.Dict:
    return {"success": False}
