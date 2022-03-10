import logging
import typing

from ckan.plugins import toolkit

logger = logging.getLogger(__name__)


def authorize_list_featured_datasets(
    context: typing.Dict, data_dict: typing.Optional[typing.Dict]
) -> typing.Dict:
    return {"success": True}
