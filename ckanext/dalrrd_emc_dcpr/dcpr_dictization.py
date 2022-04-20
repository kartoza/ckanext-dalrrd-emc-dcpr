"""
NOTE: These have been implemented in the spirit of `ckan.lib.dictization.model_dictize`

These dictize functions take a DCPR object (which is also a CKAN domain object) and
convert it to a dictionary, including related objects (e.g. for Package it
includes PackageTags, PackageExtras, PackageGroup etc).

The basic recipe is to call:

    dictized = ckanext.dalrrd_emc_dcpr.dcpr_dictization.table_dictize(domain_object)

which builds the dictionary by iterating over the table columns.

"""

import typing

from ckan.lib.dictization import table_dictize

from .constants import DCPR_REQUEST_DATASET_TYPE
from .model.dcpr_request import DCPRRequest


def dcpr_request_dictize(
    dcpr_request: DCPRRequest, context: typing.Dict
) -> typing.Dict:
    result_dict = table_dictize(dcpr_request, context)
    result_dict["type"] = DCPR_REQUEST_DATASET_TYPE
    return result_dict
