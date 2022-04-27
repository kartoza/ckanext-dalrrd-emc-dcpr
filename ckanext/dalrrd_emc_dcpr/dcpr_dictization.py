"""
NOTE: These have been implemented in the spirit of `ckan.lib.dictization`

These dictize functions take a DCPR object (which is also a CKAN domain object) and
convert it to a dictionary, including related objects (e.g. for Package it
includes PackageTags, PackageExtras, PackageGroup etc).

The basic recipe is to call:

    dictized = ckanext.dalrrd_emc_dcpr.dcpr_dictization.table_dictize(domain_object)

which builds the dictionary by iterating over the table columns.

"""

import typing

import ckan.lib.dictization as ckan_dictization

from .model import dcpr_request as dcpr_request_model


def dcpr_request_dictize(
    dcpr_request: dcpr_request_model.DCPRRequest, context: typing.Dict
) -> typing.Dict:
    result_dict = ckan_dictization.table_dictize(dcpr_request, context)
    return result_dict


def dcpr_request_dict_save(data_dict: typing.Dict, context: typing.Dict):
    if "request_date" in data_dict:
        del data_dict["request_date"]
    dcpr_request = ckan_dictization.table_dict_save(
        data_dict, dcpr_request_model.DCPRRequest, context
    )
    dcpr_request_dataset_list_save(
        data_dict.get("dcpr_datasets", []), dcpr_request, context
    )
    return dcpr_request


def dcpr_request_dataset_list_save(
    datasets: typing.List[typing.Dict], dcpr_request, context: typing.Dict
) -> None:
    for dataset_dict in datasets:
        dataset_dict["dcpr_request_id"] = dcpr_request.csi_reference_id
        dcpr_dataset_save(dataset_dict, context)


def dcpr_dataset_save(dcpr_dataset_dict: typing.Dict, context: typing.Dict):
    model = context["model"]
    session = context["session"]
    id_ = dcpr_dataset_dict.get("dataset_id")
    obj = None
    if id_:
        obj = session.query(model.DCPRRequestDataset).get(id_)
    if not obj:
        obj = model.DCPRRequestDataset()
    obj.from_dict(dcpr_dataset_dict)
    session.add(obj)
    return obj
