import typing
import uuid
from copy import deepcopy
from ...constants import (
    DATASET_SUBFIELDS_MAPPING,
    STATIC_METADATA_RECORD_FIELDS,
    USED_ACTIONS_SUBFIELDS,
    METADATA_STANDARD_NAME_AND_VERSION_FIELDS,
)

import ckan.plugins.toolkit as toolkit


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
        if type(org_list) == str:
            return data_dict
        owner_org = org_list[0]
        contact_org = org_list[1]
        data_dict["owner_org"] = owner_org
        data_dict[USED_ACTIONS_SUBFIELDS["contact_organisation"]] = contact_org
        return data_dict
    except Exception as e:
        raise RuntimeError(e)
        pass


def add_static_fields(data_dict: dict) -> dict:
    """
    some fields are required by sans1878,
    and they don't change in value (e.g. metadata
    contact organisation role which is point of contact)
    """
    data_dict.update(STATIC_METADATA_RECORD_FIELDS)
    return data_dict


def add_uuid_to_newly_created_datasets(data_dict: dict):
    """
    adding uuid to the named url
    to avoid drafts datasets name clash,
    dataset name slug field was required to
    be changed by the client.
    """
    title = data_dict.get("title")
    name = remove_special_characters_from_package_url(title)
    if name is not None:
        name = name.replace(" ", "-")
        uuid_str = str(uuid.uuid4())
        name += "-" + uuid_str
        name = name.lower()
        return [uuid_str, name]


def update_dataset_name_uuid(data_dict: dict):
    """
    once we have a dataset,
    the name should hold the
    same id of the dataset at
    it's end instead of the one
    used during creation.
    """
    # dataset_id = data_dict.get("pkg_name")
    # name = data_dict.get("id")
    dataset_id = data_dict.get("id")
    name = data_dict.get("name")
    if name is not None:
        _uuid = name[-36:]
        name = name.replace(_uuid, dataset_id)
        data_dict["name"] = name
        return data_dict


def remove_special_characters_from_package_url(url):
    """
    special characters are not
    accepted by CKAN for dataset
    urls, replace them
    """
    special_chars = "!\"”'#$%&'()*+,-./:;<=>?@[\]^`{|}~.[]"
    if url is not None:
        for i in url:
            if i in special_chars:
                url = url.replace(i, "-")

        return url


def switch_from_draft_to_active(data_dict: dict):
    old_dataset = toolkit.get_action("package_show")(data_dict={"id": data_dict["id"]})
    shared_items = {
        k: data_dict[k]
        for k in data_dict
        if k in old_dataset and data_dict[k] == old_dataset[k]
    }
    # if it's changed from draft to active
    non_shared = []
    for k in data_dict:
        if k not in shared_items.keys():
            non_shared.append(k)
            if k == "state":
                if old_dataset[k] == "draft":
                    return True


def add_metadata_name_and_version(data_dict):
    """
    with package create, repeated
    subfields are not applying
    converters, handled here
    """

    def default_metadata_standard_name(value):
        """
        returns SANS1878 as the default
        metadata standard name.
        """
        if value == "" or value is None:
            return "SANS 1878-1:2011"
        return value

    def default_metadata_standard_version(value):
        """
        returns SANS1878 as the default
        metadata standard name.
        """
        if value == "" or value is None:
            return "1.1"
        return value

    try:
        data_dict["metadata_standard"][0]["name"] = default_metadata_standard_name(
            data_dict["metadata_standard"][0]["name"]
        )
        data_dict["metadata_standard"][0][
            "version"
        ] = default_metadata_standard_version(
            data_dict["metadata_standard"][0]["version"]
        )

    except KeyError:

        metadata_standard_name_field = METADATA_STANDARD_NAME_AND_VERSION_FIELDS[
            "metadata_name"
        ]
        metadata_standard_version_field = METADATA_STANDARD_NAME_AND_VERSION_FIELDS[
            "metadata_version"
        ]

        metadata_standard_name = data_dict.get(metadata_standard_name_field)
        metadata_standard_version = data_dict.get(metadata_standard_version_field)

        data_dict[metadata_standard_name_field] = default_metadata_standard_name(
            metadata_standard_name
        )
        data_dict[metadata_standard_version_field] = default_metadata_standard_version(
            metadata_standard_version
        )

    return data_dict


def apply_pre_create_handlers(data_dict):
    """
    functions applied before
    creating the package
    """
    pkg_id, named_url = add_uuid_to_newly_created_datasets(data_dict)
    # package create calls package_dict_save which checks first if there is an id or creates uuid instead, we are doing it here
    data_dict["id"] = pkg_id
    data_dict["name"] = named_url
    data_dict = set_contact_org(data_dict)
    return data_dict


def apply_update_handlers(data_dict: dict):
    """
    these will be called every time
    package update called
    pckage update is called
    multiple times after package create
    """
    data_dict = add_static_fields(data_dict)
    data_dict = set_contact_org(data_dict)
    data_dict = add_metadata_name_and_version(data_dict)
    return data_dict


# test_suite = {"contact-1-organization_role":"organization role value","lineage-0-statement":"lineage statement value",
# "maintenance_information-3-maintenance_date":"maintenance information date", "reference_system_additional_info-0-temporal_reference":"temporal info"}

# print(handle_repeating_subfields_naming(test_suite))
