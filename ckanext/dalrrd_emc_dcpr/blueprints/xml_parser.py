from pydoc import describe
from flask import request, Response, abort, redirect, jsonify, Blueprint
from ckan.plugins import toolkit
import xml.dom.minidom as dom
import logging
import json
from datetime import datetime
from ..constants import DATASET_MINIMAL_SET_OF_FIELDS as xml_minimal_set

# About this Blueprint:
# -------------
# parsing xml file to extract info
# necessary to create a dataset,
# calls dataset create action.

logger = logging.getLogger(__name__)

xml_parser_blueprint = Blueprint(
    "xml_parser",
    __name__,
    url_prefix="/dataset/xml_parser",
    template_folder="templates",
)


@xml_parser_blueprint.route("/", methods=["GET", "POST"])
def extract_files():
    """
    the blueprint allows for multiple
    files to be sent at once, extract
    each and call parse_xml_dataset.
    retutn success after all files
    parsed.
    """
    # files = request.files.to_dict()
    xml_files = request.files.getlist("xml_dataset_files")
    # loggin the request files.
    logger.debug("from xml parser blueprint, the xmlfiles object should be:", xml_files)

    for _file in xml_files:
        check_results = parse_xml_dataset_upload(_file)
        if check_results["state"] == False:
            return jsonify(check_results["msg"])
    return Response(status=200)


def check_file_fields(xml_files) -> list:
    """
    check if the each xml file holds
    fields more than the maximum
    set of fields, if so raises
    an error.

    returns:
    -----
    a list of parsed dom root
    elements.
    """
    roots = []
    for xml_file in xml_files:
        dom_ob = dom.parse(xml_file)
        root = dom_ob.firstChild
        roots.append(root)
        if root.hasChildNodes():
            pass
    return roots


def parse_xml_dataset_upload(xml_file):
    """
    parse xml file via dom lib,
    """
    logger.debug("from xml parser blueprint", xml_file)
    dom_ob = dom.parse(xml_file)
    root = dom_ob.firstChild
    fields_ob = {}
    if root.hasChildNodes():
        for field in root.childNodes:
            # extract_tags(field)
            # nodeType is end of line character,
            # we need to skip it
            if field.nodeType != 3 and field.tagName == "reference_date":
                date_field = handle_date_field(field)
                fields_ob.update(date_field)
            elif field.nodeType != 3:
                fields_ob.update({field.tagName: field.childNodes[0].data})
    slug_url_field = fields_ob["title"].replace(" ", "-")
    fields_ob.update({"name": slug_url_field})
    # checks
    # minimal set check
    minimal_check = minimal_set_check(fields_ob, xml_minimal_set)
    if minimal_check["state"] == False:
        return minimal_check
    create_action = toolkit.get_action("package_create")
    create_action(data_dict=fields_ob)


def handle_date_field(date_field):
    """
    returns a date from iso-string
    YY-MM-DDTHH:MM:SS
    """
    date_ob = {}
    date_string = date_field.childNodes[0].data
    date_ob["iso_date"] = datetime.fromisoformat(date_string)

    return {date_field.tagName: date_ob["iso_date"]}


def minimal_set_check(field_ob: dict, minimal_set: list):
    """
    getting all the tag names
    to check if the satisfy the
    minimal set of required tags
    """
    available_tags = list(field_ob.keys())
    for tag in minimal_set:
        if tag not in available_tags:
            # flash and abort
            msg = f"{tag} is a required missing field"
            return {"state": False, "msg": msg}
    return {"state": True}


def missing_values_check():
    """
    the tag is there, but the
    value is not
    """
    pass


def additional_fields_check(field_name):
    """
    checking if the provided field
    is more than the
    """


# xml_tags = []
# def extract_tags(root):
#     """
#         getting all the tag names
#         to check if the satisfy the
#         minimal set of required tags
#     """
#     if root.hasChildNodes():
#         xml_tags.append(root.tagName)
#         for field in root.childNodes:
#             if field.nodeType != 3:
#                 extract_tags(field)
