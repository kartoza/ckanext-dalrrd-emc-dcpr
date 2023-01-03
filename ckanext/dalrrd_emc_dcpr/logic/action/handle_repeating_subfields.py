from copy import deepcopy
import re

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
    repeating_fields = [
        "contact",
        "lineage",
        "distribution",
        "maintenance_information",
        "reference_system_additional_info",
    ]
    new_data_dict = deepcopy(data_dict)
    for k in data_dict:
        for key in repeating_fields:
            if k.startswith(key):
                key_initials = f"{key}-\w+-"
                print(key_initials)
                subfield_name = re.sub(key_initials, "", k)
                print(subfield_name)
                new_key = f"{key}_" + subfield_name
                new_data_dict[new_key] = new_data_dict.pop(k)
    return new_data_dict


# test_suite = {"contact-1-organization_role":"organization role value","lineage-0-statement":"lineage statement value",
# "maintenance_information-3-maintenance_date":"maintenance information date", "reference_system_additional_info-0-temporal_reference":"temporal info"}

# print(handle_repeating_subfields_naming(test_suite))
