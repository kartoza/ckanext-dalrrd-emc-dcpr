from flask import request, Response, jsonify, Blueprint
from ckan.plugins import toolkit
import xml.dom.minidom as dom
import logging
from datetime import datetime
from ..constants import DATASET_MINIMAL_SET_OF_FIELDS as xml_minimum_set, DATASET_FULL_SET_OF_FIELDS as xml_full_set
import os
# About this Blueprint:
# -------------
# parsing xml file to extract info
# necessary to create a dataset,
# calls dataset create action.
# use it as root_url/dataset/xml_parser/

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
    check_result = check_file_fields(xml_files)
    if check_result is None:
        return "something went wrong during dataset creation!"
    if check_result["state"] == False:
        return jsonify(check_result["msg"])
    return Response(response="package created !", status=200)


def check_file_fields(xml_files) -> dict:
    """
    performs different checks over
    the xml files.

    returns:
    -----
    object with status: False and a message
    or status:True.
    """
    root = None
    for xml_file in xml_files:
        # has data check
        dataset = file_has_xml_dataset(xml_file)
        if dataset["state"]:
            root = dataset["root"]
        else:
            return dataset["msg"]
        if root is not None:
            # return and object of the root
            root = return_object_root(root)
            # has field more than maximum set
            maximum_fields_check_ob = maximum_fields_check(root)
            if maximum_fields_check_ob["state"] == False:
                return {"state":False, "msg":maximum_fields_check_ob["msg"]}
            # has field less than minimum set    
            minimum_set_check_ob = minimum_set_check(root)
            if minimum_set_check_ob["state"] == False:
                return {"state":False, "msg":minimum_set_check_ob["msg"]}
            root = handle_date_fields(root)
            create_ckan_dataset(root)
            # things went ok
            return {"state":True}
        else:
            return {"state":False, "msg":"something went wrong during dataset creation"}


def file_has_xml_dataset(xml_file):
    """
    parses the file, 
    checks if file has a
    dataset within it and 
    returns it.
    """
    dom_ob = dom.parse(xml_file)
    root = dom_ob.firstChild
    if root.hasChildNodes():
        return {"state":True,"root":root}
    else:
        return {"state":False, "msg":f"file {xml_file.filename} is empty!"}

def return_object_root(root):
    """
    transform the xml dom
    root into an object of
    tag_name:tag_value
    """
    ob_root = {}
    for field in root.childNodes:
        if field.nodeType != 3:
            ob_root[field.tagName] = field.childNodes[0].data
    
    return ob_root

def maximum_fields_check(root_ob):
    """
    checking if the provided field
    is more than the maximum set
    of EMC datasets fields.
    """
    root_ob_keys = root_ob.keys()
    for field in root_ob_keys:
        if field not in xml_full_set:
                return {"state":False, "msg":f"field \"{field}\" "+ 
                "is not within the maximum set of allowed xml fields"} 
    return {"state":True}

def minimum_set_check(root_ob: dict):
    """
    checking if the xml file fields
    has the minimum required set.
    """
    # adding field "name" later dynamically 
    for tag in xml_minimum_set:
        if tag not in root_ob:
            if tag !="name":
                msg = f"{tag} is a required missing field"
                return {"state": False, "msg": msg}
    return {"state": True}

def handle_date_fields(root_ob):
    """
    date fields need to be 
    iso compliant inorder
    to create the package,
    transform date strings
    to dates. 
    """
    date_fields = ["reference_date"]
    for field in date_fields:
        iso_date_field = handle_date_field(root_ob[field])
        root_ob.update(iso_date_field)
    return root_ob


def create_ckan_dataset(root_ob):
    """
    create package via ckan api's
    package_create action.
    """
    logger.debug("from xml parser blueprint", root_ob)
    slug_url_field = root_ob["title"].replace(" ", "-")
    root_ob.update({"name": slug_url_field})
    create_action = toolkit.get_action("package_create")
    create_action(data_dict=root_ob)
    return {"state":True}

def handle_date_field(date_field):
    """
    returns a date from iso-string
    YY-MM-DDTHH:MM:SS
    """
    iso_date = datetime.fromisoformat(date_field)
    return {date_field: iso_date}