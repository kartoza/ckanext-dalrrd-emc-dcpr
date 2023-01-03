import os
from pycsw.core import util
from pycsw.core.etree import etree

NAMESPACE = "sans1878"
NAMESPACES = {"sans": NAMESPACE}

XPATH_MAPPINGS = {
    "pycsw:Identifier": "sans:id",
    "pycsw:Title": "sans:title",
    "pycsw:Abstract": "sans:abstract",
    "pycsw:Purpose": "sans:purpose",
    "pycsw:Status": "sans:completed",
    "pycsw:Contact_organisationalRole": "sans:contact_organisational_role",
    "pycsw:CI_ResponsiblePartyOrganisationName": "sans:ci_responsible_party_organisation_name",
    "pycsw:DatasetLanguage": "sans:dataset_language",
    "pycsw:MetadataLanguage": "sans:metadata_language",
    "pycsw:DatasetCharacterSet": "sans:dataset_character_set",
    "pycsw:MetadataCharacterSet": "sans:metadata_character_set",
    "pycsw:Lineage": "sans:lineage",
    "pycsw:MetadataDateStamp": "sans:metadata_date_stamp",
    "pycsw:ReferenceDate": "sans:reference_date",
    "pycsw:TopicCategory": "sans:topiccategory",
    "pycsw:PublicationDate": "sans:published",
    "pycsw:Keywords": "sans:keywords",
}


def write_record(result, esn, context, url=None):
    """Return csw:SearchResults child as lxml.etree.Element"""

    typename = util.getqattr(
        result, context.md_core_model["mappings"]["pycsw:Typename"]
    )

    if esn == "full" and typename == "sans:entry":
        # dump record as is and exit
        return etree.fromstring(
            util.getqattr(result, context.md_core_model["mappings"]["pycsw:XML"]),
            context.parser,
        )

    node = etree.Element(util.nspath_eval("sans:entry", NAMESPACES), nsmap=NAMESPACES)
    # node.attrib[util.nspath_eval('xsi:schemaLocation', context.namespaces)] = \
    #         '%s http://www.kbcafe.com/rss/atom.xsd.xml' % NAMESPACES['atom']

    # author
    val = util.getqattr(result, context.md_core_model["mappings"]["pycsw:Creator"])
    if val:
        author = etree.SubElement(node, util.nspath_eval("atom:author", NAMESPACES))
        etree.SubElement(author, util.nspath_eval("atom:name", NAMESPACES)).text = val

    # keywords
    val = util.getqattr(result, context.md_core_model["mappings"]["pycsw:Keywords"])

    if val:
        for kw in val.split(","):
            etree.SubElement(
                node, util.nspath_eval("sans:keywords", NAMESPACES), term=kw
            )

    for qval in ["pycsw:Contributor", "pycsw:Identifier"]:
        val = util.getqattr(result, context.md_core_model["mappings"][qval])
        if val:
            etree.SubElement(
                node, util.nspath_eval(XPATH_MAPPINGS[qval], NAMESPACES)
            ).text = val
            if qval == "pycsw:Identifier":
                etree.SubElement(
                    node, util.nspath_eval("dc:identifier", context.namespaces)
                ).text = val

    rlinks = util.getqattr(result, context.md_core_model["mappings"]["pycsw:Links"])
    if rlinks:
        for link in util.jsonify_links(rlinks):
            url2 = etree.SubElement(
                node, util.nspath_eval("sans:link", NAMESPACES), href=link["url"]
            )

            if link.get("description") is not None:
                url2.attrib["title"] = link["description"]

            if link.get("protocol") is not None:
                url2.attrib["type"] = link["protocol"]

            if link.get("function") is not None:
                url2.attrib["rel"] = link["function"]

    etree.SubElement(
        node,
        util.nspath_eval("sans:link", NAMESPACES),
        href="%s?service=CSW&version=2.0.2&request=GetRepositoryItem&id=%s"
        % (
            url,
            util.getqattr(
                result, context.md_core_model["mappings"]["pycsw:Identifier"]
            ),
        ),
    )

    # sans:title
    el = etree.SubElement(
        node, util.nspath_eval(XPATH_MAPPINGS["pycsw:Title"], NAMESPACES)
    )
    val = util.getqattr(result, context.md_core_model["mappings"]["pycsw:Title"])
    if val:
        el.text = val

    # sans:updated
    el = etree.SubElement(
        node, util.nspath_eval(XPATH_MAPPINGS["pycsw:Modified"], NAMESPACES)
    )
    val = util.getqattr(result, context.md_core_model["mappings"]["pycsw:Modified"])
    if val:
        el.text = val
    else:
        val = util.getqattr(
            result, context.md_core_model["mappings"]["pycsw:InsertDate"]
        )
        el.text = val

    for qval in [
        "pycsw:PublicationDate",
        "pycsw:AccessConstraints",
        "pycsw:Source",
        "pycsw:Abstract",
    ]:
        val = util.getqattr(result, context.md_core_model["mappings"][qval])
        if val:
            etree.SubElement(
                node, util.nspath_eval(XPATH_MAPPINGS[qval], NAMESPACES)
            ).text = val

    # sans:purpose
    el = etree.SubElement(
        node, util.nspath_eval(XPATH_MAPPINGS["pycsw:Purpose"], NAMESPACES)
    )
    val = util.getqattr(result, context.md_core_model["mappings"]["pycsw:Purpose"])
    if val:
        el.text = val

    # sans:purpose
    el = etree.SubElement(
        node, util.nspath_eval(XPATH_MAPPINGS["pycsw:MetadataCharacterSet"], NAMESPACES)
    )
    val = util.getqattr(
        result, context.md_core_model["mappings"]["pycsw:MetadataCharacterSet"]
    )
    if val:
        el.text = val

    # bbox extent
    # val = util.getqattr(result, context.md_core_model['mappings']['pycsw:BoundingBox'])
    # bboxel = write_extent(val, context.namespaces)
    # if bboxel is not None:
    #     node.append(bboxel)

    return node


#  data_dict = {
#         "equivalent_scale": "500",
#         "spatial_representation_type": "001",
#         "spatial_reference_system": "EPSG:4326",
#         "metadata_date_stamp": "2020-01-01",
#     }
