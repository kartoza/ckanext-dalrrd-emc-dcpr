"""
This file follows the convention used in the dcpr_dictization to save the error reports
"""

import logging
import typing

import ckan.lib.dictization as ckan_dictization

from .model import error_report as error_report_model

logger = logging.getLogger(__name__)


def error_report_dict_save(validated_data_dict: typing.Dict, context: typing.Dict):
    if "request_date" in validated_data_dict:
        del validated_data_dict["request_date"]

    # vanilla ckan's table_dict_save expects the input data_dict to have an `id` key,
    # otherwise it will not be able to find pre-existing table rows
    validated_data_dict["id"] = validated_data_dict.get("csi_reference_id")
    error_report = ckan_dictization.table_dict_save(
        validated_data_dict, error_report_model.ErrorReport, context
    )
    context["session"].flush()

    return error_report


def error_report_dictize(
    error_report: error_report_model.ErrorReport,
    context: typing.Dict,
) -> typing.Dict:
    result_dict = ckan_dictization.table_dictize(error_report, context)

    if context.get("dictize_for_ui", False):
        result_dict.update(
            {"owner": error_report.owner.name, "record": error_report.record}
        )

    return result_dict
