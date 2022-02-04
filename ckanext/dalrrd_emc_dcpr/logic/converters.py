"""Custom converters for SASDI EMC"""

import typing
import logging

import ckan.lib.navl.dictization_functions as df
from ckan import model
from ckan.plugins import toolkit

from .. import constants

logger = logging.getLogger(__name__)


def emc_convert_to_tags(vocab):
    """Re-implementation of the stock CKAN convert_to_tags converter"""

    def callable(key, data, errors, context):
        logger.warning(
            f"---------------- inside custom convert_to_tags. locals: {locals()=}"
        )
        new_tags = data.get(key)
        logger.warning(f"---------------- new_tags: {new_tags=}")
        if not new_tags:
            return
        if isinstance(new_tags, str):
            new_tags = [new_tags]

        # get current number of tags
        n = 0
        for k in data.keys():
            if k[0] == "tags":
                n = max(n, k[1] + 1)

        v = model.Vocabulary.get(vocab)
        if not v:
            raise df.Invalid(toolkit._('Tag vocabulary "%s" does not exist') % vocab)
        context["vocabulary"] = v

        for tag in new_tags:
            toolkit.get_validator("tag_in_vocabulary_validator")(tag, context)

        for num, tag in enumerate(new_tags):
            data[("tags", num + n, "name")] = tag
            data[("tags", num + n, "vocabulary_id")] = v.id

    return callable


def emc_convert_from_tags(vocab):
    """Re-implementation of the stock CKAN convert_from_tags converter"""

    def callable(key, data, errors, context):
        logger.warning(
            f"----------------------- inside custom convert_from_tags. locals: {locals()=}"
        )
        v = model.Vocabulary.get(vocab)
        if not v:
            raise df.Invalid(toolkit._('Tag vocabulary "%s" does not exist') % vocab)

        tags = []
        for k in data.keys():
            if k[0] == "tags":
                if data[k].get("vocabulary_id") == v.id:
                    name = data[k].get("display_name", data[k]["name"])
                    tags.append(name)
        logger.warning(f"setting data[{key}] to {tags}")
        data[key] = tags

    return callable


def emc_convert_known_vocabulary_tag_value_to_select_label(vocabulary_name: str):
    def _inner(key, flattened_data, errors, context):
        logger.debug(f"inside custom convert_tag_to_select. locals: {locals()=}")
        if vocabulary_name == constants.ISO_TOPIC_CATEGOY_VOCABULARY_NAME:
            for category_value, category_label in constants.ISO_TOPIC_CATEGORIES:
                if flattened_data[key] == category_value:
                    result = category_label
                    break
            else:
                result = ""
        flattened_data[key] = result

    return _inner
