import string
import random
import re
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import flash_success


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
    for k in data_dict:
        if k not in shared_items.keys():
            if k == "state":
                if old_dataset[k] == "draft":
                    return data_dict
    old_version = old_dataset.get("version")
    new_version = data_dict.get("version")
    url = data_dict.get("name")
    new_version = numbering_version(url)
    # create new dataset if the status is completed
    if old_dataset.get("status") == "completed":
        generated_id = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(6)
        )
        update_dataset_title_and_url(new_version, generated_id, data_dict)
        result = toolkit.get_action("package_create")(context, data_dict)
        flash_success("new version is created, updating the existing one !")
        return result


def numbering_version(url):
    """
    handle the numbering
    logic of the new
    version, incrementing
    the last one by one
    """
    match = re.search(r"[\d+]$", url)
    version_number = "0"
    if match is None:
        version_number = "2"
    else:
        version_number = str(int(match.group()) + 1)

    return version_number


def get_previous_versions(url, context):
    """
    TODO: i need to get the highest
    number of previous versions in case
    the user updated the version from the
    original dataset, which results in creating
    a new version with the number 2.
    get the pervious
    versions of the dataset
    """
    url_name, version = url.split("_v_")
    packages = toolkit.get_action("package_list")()


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
        if i in "!”#$%&'()*+,-./:;<=>?@[\]^`{|}~.":
            new_url = new_url.replace(i, "_")
    data_dict.update({"id": new_id, "title": new_title, "name": new_url})
    return data_dict


def search_and_update(title_or_url, new_version):
    """
    uses regex to find version
    and update the title and
    url accordingly
    """
    delimeter = ""
    str_to_substitute = ""
    if title_or_url.get("type") == "title":
        delimeter = "."
        str_to_substitute = title_or_url.get("title")
    else:
        delimeter = "-"
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


# def remove_special_characters_from_package_url(url:str):
#     """
#     special characters are not
#     accepted by CKAN for dataset
#     urls, replace them
#     """
#     return re.sub("!\"”'#$%&'()*+,-./:;<=>?@[\]^`{|}~.","",url)
