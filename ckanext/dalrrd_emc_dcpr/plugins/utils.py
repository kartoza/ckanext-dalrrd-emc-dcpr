"""
# this file holds modules used
# by emc_dcpr plugin for different
# functionalities. these modules are
# different from helper functions as
# they aren't used by the UI.
# """


def handle_search(search_params):
    """
    we use combine -AND operator-
    search params when they are from
    the same category "e.g. 2 different
    organizations", and use OR opertaor
    for different categories.
    """
    # \[.*\]
    # lstrip removes leading spaces
    search_param = search_params["fq"].lstrip()

    fq_list = skip_brackets(search_param)

    # fq_list = search_param.split()  # the default is space
    fq_dict = {}
    if len(fq_list) <= 1:
        return search_params["fq"]
    for idx, item in enumerate(fq_list):
        # try:
        #     key_value_pair = item.split(":")
        #     if key_value_pair[0] not in fq_dict:
        #         fq_dict[key_value_pair[0]] = key_value_pair[1]
        # except:
        #     continue

        try:
            if idx > 0:
                fq_list[idx] = " OR " + fq_list[idx] + " "

        except:
            continue
    if len(fq_list) > 0:
        search_params["fq"] = " ".join(item for item in fq_list)

    return search_params["fq"]


# import re

# string = "-dataset_type:harvest reference_date:[2022-10-27T00:00:00Z TO *]"
# # match = re.search(r"[\[.*\]]", string)
# for match in re.finditer(r"\[.*?\]", string):
#     print(match.group(), match.start())


# if match:
#     print(match)


def skip_brackets(search_param: str):
    """
    split the search param while
    skipping the spaces between
    brackets and between
    doubled quotes (e.g.
    the sasdi theme
    "Administrative boundaries 1"
    )
    """
    lbracket, rbracket = "[", "]"
    brackets_num = 0
    dbl_quotes_num = 0
    sep, sep_idx = " ", [0]

    for idx, char in enumerate(search_param):
        if char == lbracket:
            brackets_num += 1
        elif char == rbracket:
            brackets_num -= 1
        elif brackets_num < 0:
            return search_param

        elif char == '"' and dbl_quotes_num == 0:
            dbl_quotes_num += 1

        elif char == '"' and dbl_quotes_num == 1:
            dbl_quotes_num -= 1

        elif brackets_num == 0 and dbl_quotes_num == 0 and char == sep:
            sep_idx.append(idx)
    # we need to slice
    sep_idx.append(len(search_param))
    # at this point the num of brackets should be 0
    if brackets_num > 0:
        return search_param

    return [search_param[i:j].strip(sep) for i, j in zip(sep_idx, sep_idx[1:])]
