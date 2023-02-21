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
import ast

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
    dconstructed_dicts = deconstruct_list_values(datasets)
    if len(dconstructed_dicts) > 1:
        for dataset_dict in dconstructed_dicts:
            dataset_dict = sepecial_fields_resolve(dataset_dict)
            dataset_dict["dcpr_request_id"] = dcpr_request.csi_reference_id
            dcpr_dataset_save(dataset_dict, context)
        return

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


def deconstruct_list_values(dataset: list) -> list:
    """
    sometimes instead of having
    multiple dicts holding different
    dcpr datasets, one dict might be
    submitted where the same key has
    a list of values
    """
    dataset_dict = dataset[0]
    titles = dataset_dict.get("proposed_dataset_title")
    lineage = dataset_dict.get("lineage_statement")
    try:
        titles = ast.literal_eval(titles)
        lineage = ast.literal_eval(lineage)

    except:
        return []
    if isinstance(titles, list) or isinstance(lineage, list):
        datasets = []
        dataset_keys = dataset_dict.keys()
        for i in range(len(titles)):
            new_dict = {}
            for key in dataset_keys:
                if isinstance(dataset_dict[key], list):  # sometimes they come as list
                    value = dataset_dict[key][i]
                else:
                    try:
                        value = ast.literal_eval(dataset_dict[key])[i]
                    except:
                        continue
                new_dict[key] = value
            datasets.append(new_dict)

        return datasets
    else:
        return []


def sepecial_fields_resolve(data_dict: dict):
    """
    there are some special fields
    like the dataset_custodian that
    needs to be converted to some
    values first
    """
    custodian_value = data_dict.get("dataset_custodian")
    if custodian_value == "E1":
        data_dict["dataset_custodian"] = True
    elif custodian_value == "E2":
        data_dict["dataset_custodian"] = False

    return data_dict
