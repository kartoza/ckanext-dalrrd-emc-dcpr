"""
NOTE: These have been implemented in the spirit of `ckan.lib.dictization`

These dictize functions take a DCPR object (which is also a CKAN domain object) and
convert it to a dictionary, including related objects (e.g. for Package it
includes PackageTags, PackageExtras, PackageGroup etc).

The basic recipe is to call:

    dictized = ckanext.dalrrd_emc_dcpr.dcpr_dictization.table_dictize(domain_object)

which builds the dictionary by iterating over the table columns.

"""

import logging
import typing

import ckan.lib.dictization as ckan_dictization

from .model import dcpr_request as dcpr_request_model

logger = logging.getLogger(__name__)


def dcpr_request_dictize(
    dcpr_request: dcpr_request_model.DCPRRequest,
    context: typing.Dict,
) -> typing.Dict:
    result_dict = ckan_dictization.table_dictize(dcpr_request, context)
    result_dict["datasets"] = []
    for dcpr_dataset in dcpr_request.datasets:
        dataset_dict = dcpr_request_dataset_dictize(dcpr_dataset, context)
        result_dict["datasets"].append(dataset_dict)
    result_dict["capture_start_date"] = result_dict["capture_start_date"].partition(
        "T"
    )[0]
    result_dict["capture_end_date"] = result_dict["capture_end_date"].partition("T")[0]
    if context.get("dictize_for_ui", False):
        result_dict.update(
            {
                "owner": dcpr_request.owner.name,
                "organization": dcpr_request.organization.name,
            }
        )
    return result_dict


def dcpr_request_dataset_dictize(
    dcpr_dataset: dcpr_request_model.DCPRRequestDataset, context: typing.Dict
) -> typing.Dict:
    return ckan_dictization.table_dictize(dcpr_dataset, context)


def dcpr_request_dict_save(validated_data_dict: typing.Dict, context: typing.Dict):
    if "request_date" in validated_data_dict:
        del validated_data_dict["request_date"]

    # vanilla ckan's table_dict_save expects the input data_dict to have an `id` key,
    # otherwise it will not be able to find pre-existing table rows
    validated_data_dict["id"] = validated_data_dict.get("csi_reference_id")
    dcpr_request = ckan_dictization.table_dict_save(
        validated_data_dict, dcpr_request_model.DCPRRequest, context
    )
    context["session"].flush()
    if context.get("updated_by") == "owner":
        # allow modification of a request's datasets only if current save was requested by the owner
        for ds in dcpr_request.datasets:
            context["session"].delete(ds)
        dcpr_request_dataset_list_save(
            validated_data_dict.get("datasets", []), dcpr_request, context
        )
    return dcpr_request


def dcpr_request_dataset_list_save(
    datasets: typing.List[typing.Dict], dcpr_request, context: typing.Dict
) -> None:
    for dataset_dict in datasets:
        dataset_dict["dcpr_request_id"] = dcpr_request.csi_reference_id
        dcpr_dataset_save(dataset_dict, context)


def dcpr_dataset_save(dcpr_dataset_dict: typing.Dict, context: typing.Dict):
    session = context["session"]
    obj = dcpr_request_model.DCPRRequestDataset()
    logger.debug(f"{dcpr_dataset_dict=}")
    obj.from_dict(dcpr_dataset_dict)
    session.add(obj)
    return obj
