from flask import request, Response, render_template, redirect, url_for, Blueprint
from ckan.plugins import toolkit
import xml.dom.minidom as dom
import logging
import json
from datetime import datetime

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
    parsing xml file to extract info
    necessary to create a dataset,
    calls dataset create action
    """
    # files = request.files.to_dict()
    xml_files = request.files.getlist("xml_dataset_files")
    logger.debug("from xml parser blueprint, the xmlfiles object should be:", xml_files)
    for _file in xml_files:
        parse_xml_dataset_upload(_file)
    return Response(status=200)


def parse_xml_dataset_upload(xml_file):
    logger.debug("from xml parser blueprint")
    dom_ob = dom.parse(xml_file)
    root = dom_ob.firstChild
    fields_ob = {}
    if root.hasChildNodes():
        for field in root.childNodes:
            # nodeType is end of line character,
            # we need to skip it
            if field.nodeType != 3 and field.tagName == "reference_date":
                date_field = handle_date_field(field)
                fields_ob.update(date_field)
            elif field.nodeType != 3:
                fields_ob.update({field.tagName: field.childNodes[0].data})
    slug_url_field = fields_ob["title"].replace(" ", "-")
    fields_ob.update({"name": slug_url_field})
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
