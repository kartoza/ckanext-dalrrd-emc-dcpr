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
    package_state = data_dict.get("state")
    if package_state is None:
        return data_dict
    if package_state is not "active":
        return data_dict

    old_dataset = toolkit.get_action("package_show")(data_dict={"id": data_dict["id"]})
    old_version = old_dataset.get("version")
    new_version = data_dict.get("version")
    url = data_dict.get("name")
    new_version = numbering_version(url, old_version, new_version)
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


def numbering_version(url, old_version, new_version):
    """
    handle the numbering
    logic of the new version
    """
    match = re.search(r"[\d+]$", url)
    if match is None:
        return "2"
    else:
        return str(int(match.group()) + 1)


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
