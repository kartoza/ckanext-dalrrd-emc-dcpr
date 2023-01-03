import string
import random
import re
import json
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import flash_success
from ckan import model

import sqlalchemy

_select = sqlalchemy.sql.select
_and_ = sqlalchemy.and_


def handle_versioning(context, data_dict):
    """
    accoring to whether the dataset
    status is completed or not, the
    update action should either create
    a new version or overwrite the
    extising dataset.
    """
    # handling the version number
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
                    return data_dict
            if k == "resources":
                return data_dict
    resources = _get_package_resource(context, data_dict)
    new_version = data_dict.get("version")
    url = data_dict.get("name")
    new_version = numbering_version(url, context, data_dict)
    # create new dataset if the status is completed
    if old_dataset.get("status") == "completed":
        generated_id = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(6)
        )
        update_dataset_title_and_url(new_version, generated_id, data_dict)
        context["ignore_auth"] = True
        data_dict["resources"] = resources
        result = toolkit.get_action("package_create")(context, data_dict)
        flash_success("new version is created, updating the existing one !")
        return result


def numbering_version(url, context, data_dict):
    """
    handle the numbering
    logic of the new
    version, incrementing
    the last one by one
    """
    previous_version = _get_previous_versions(url, context, data_dict)
    if previous_version == 0:
        version_number = "2"
    else:
        version_number = previous_version + 1

    return str(version_number)


def _get_previous_versions(url, context, data_dict):
    """
    TODO: i need to get the highest
    number of previous versions in case
    the user updated the version from the
    original dataset, which results in creating
    a new version with the number 2.
    get the pervious
    versions of the dataset
    """
    if "_v_" in url:
        url_name, version = url.split("_v_")
    else:
        url_name = url
    # instead of pulling all the packages when can just make a query to pull
    # the packages with names starts with what we have
    model = context["model"]
    # packages = toolkit.get_action("package_list")(context=context,data_dict=data_dict) # check if this needs context
    package_table = model.package_table
    col = package_table.c.name
    query = _select([col])
    query = query.where(
        package_table.c.state == "active",
    )
    packages = [r[0] for r in query.execute()]
    # raise RuntimeError(packages)
    previous_versions = []
    for pack in packages:
        if pack.startswith(url_name):
            if "_v_" in pack:
                url_name, version_num = pack.split("_v_")
                try:
                    version_num = int(version_num)
                    previous_versions.append(version_num)
                except:
                    # couldn't get the version number
                    pass
    # raise RuntimeError(previous_versions)
    if len(previous_versions) > 0:
        return max(previous_versions)
    else:
        # there isn't any previous versions
        return 0


def update_dataset_title_and_url(
    new_version: str, generated_id: str, data_dict: dict
) -> dict:
    """
    set the name and the url for
    the new version.
    """
    id = data_dict.get("id")
    new_id = ""
    if id is not None:
        new_id = id + "_version_num_" + new_version + "_" + generated_id
    new_title = search_and_update(
        {"type": "title", "title": data_dict.get("title")}, new_version
    )
    new_url = search_and_update(
        {"type": "url", "url": data_dict.get("name")}, new_version
    )
    for i in new_url:
        if i in "!”#$%&'()*+,./:;<=>?@[\]^`{|}~.":
            new_url = new_url.replace(i, "_")
    data_dict.update({"id": new_id, "title": new_title, "name": new_url})
    return data_dict


def search_and_update(title_or_url, new_version):
    """
    uses regex to find version (num) at the end of
    string and substitute it, either in the title
    and/or url, the title
    has a dot in it's struct and
    the name (url) has a dash
    """
    delimeter = ""
    str_to_substitute = ""
    if title_or_url.get("type") == "title":
        delimeter = "."
        str_to_substitute = title_or_url.get("title")
    else:
        delimeter = "_"
        str_to_substitute = title_or_url.get("url")
    # ends with _v.digit
    match = re.search(r"_v[._][\d$]", str_to_substitute)
    if match is not None:
        str_to_substitute = re.sub(
            r"_v[._][\d]+$", f"_v{delimeter}{new_version}", str_to_substitute
        )
    else:
        # first time to change the versions
        str_to_substitute += f"_v{delimeter}" + new_version
    return str_to_substitute


def _get_package_resource(context, data_dict: dict):
    """
    getting the package resources
    """
    model = context["model"]
    package_id = data_dict.get("pkg_name")
    q = f""" select url, name, description, format, extras from resource where package_id='{package_id}'"""
    result = model.Session.execute(q)
    resources_results = result.fetchall()
    resources = []
    if len(resources_results) > 0:
        for res in resources_results:
            flattend_resource = _flatten_resource_extras(
                {
                    "url": res[0],
                    "name": res[1],
                    "description": res[2],
                    "format": res[3],
                    "extras": res[4],
                }
            )
            resources.append(flattend_resource)
        return resources


def _flatten_resource_extras(resource: dict):
    """
    returns the fields and values
    contained in resource_extra
    """
    if resource.get("extras") is not None:
        extras = json.loads(resource["extras"])
        for key, value in extras.items():
            resource[key] = value
        return resource


# def remove_special_characters_from_package_url(url:str):
#     """
#     special characters are not
#     accepted by CKAN for dataset
#     urls, replace them
#     """
#     #return re.sub("!\"”'#$%&'()*+,-./:;<=>?@[\]^`{|}~.","",url)
#     for i in url:
#         if i in "":
#             url.replace(i,"")
