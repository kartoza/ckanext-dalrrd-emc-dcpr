import typing
from copy import deepcopy
from ...constants import (
    DATASET_SUBFIELDS_MAPPING,
    STATIC_METADATA_RECORD_FIELDS,
    USED_ACTIONS_SUBFIELDS,
)

"""
ckan scheming gives repeating subfields
the naming of fieldname-0*-subfieldname
the number * can change accoring to the
number of repeating subfields, this schema
may affect how the field is going to be
referenced from other services related to
EMC, we are changing this naming here.
"""

# unfortunatley this doesn't get saved if you changed the naming
# and not retrieved from the database, something related to
# ckanext-scheming


def handle_repeating_subfields_naming(data_dict: dict):
    """
    change the naming of repeating subfields from
    fieldname-0-subfieldname
    to fieldname_subfieldname
    """
    data_dict_cp = deepcopy(data_dict)
    for k in data_dict_cp:
        try:
            db_field_name = DATASET_SUBFIELDS_MAPPING[k]
            data_dict[db_field_name] = data_dict.pop(k)
        except KeyError:
            pass
    return data_dict


def set_contact_org(data_dict):
    """
    if the snippet used for
    getting the owner org
    used with other field
    the owner org will have
    two values, we are using
    a modified version of the
    snippet with contact org
    and we need to separate the
    two values
    """
    data_dict_cp: typing.Dict[str, list[str]] = deepcopy(data_dict)
    try:
        org_list: list[str] = data_dict_cp.get("owner_org")
        owner_org = org_list[0]
        contact_org = org_list[1]
        data_dict["owner_org"] = owner_org
        data_dict[USED_ACTIONS_SUBFIELDS["contact_organisation"]] = contact_org
        return data_dict
    except:
        pass


def add_static_fields(data_dict: dict) -> dict:
    """
    some fields are required by sans1878,
    and they don't change in value (e.g. metadata
    contact organisation role which is point of contact)
    """
    data_dict.update(STATIC_METADATA_RECORD_FIELDS)
    return data_dict


# test_suite = {"contact-1-organization_role":"organization role value","lineage-0-statement":"lineage statement value",
# "maintenance_information-3-maintenance_date":"maintenance information date", "reference_system_additional_info-0-temporal_reference":"temporal info"}

# print(handle_repeating_subfields_naming(test_suite))
