"""
custom file, holds modules used directly
by emc_dcpr plugin for different
functionalities. different from
helper functions as they aren't
used by the UI.
"""


def handle_search(search_params):
    """
    we need to combine -AND operator-
    search params when they are from
    the same category "e.g. 2 different
    organizations", and use OR opertaor
    for different categories.
    """
    fq_list = search_params["fq"].split()  # the default is space
    fq_dict = {}
    for idx, item in enumerate(fq_list):
        key_value_pair = item.split(":")
        if key_value_pair[0] not in fq_dict:
            fq_dict[key_value_pair[0]] = key_value_pair[1]
        else:
            fq_list[idx] = " OR " + fq_list[idx] + " "
    search_params["fq"] = " ".join(item for item in fq_list)
    return search_params["fq"]
