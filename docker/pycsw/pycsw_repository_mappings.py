"""Mappings from CKAN to pycsw
This file is used by the EMC's pycsw instance in order to expose existing catalog
records via pycsw.
"""

from sqlalchemy.schema import PrimaryKeyConstraint

MD_CORE_MODEL = {
    "column_constraints": (PrimaryKeyConstraint("identifier"),),
    "typename": "pycsw:CoreMetadata",
    "outputschema": "http://pycsw.org/metadata",
    "mappings": {
        "pycsw:Identifier": "identifier",
        # CSW typename (e.g. csw:Record, md:MD_Metadata)
        "pycsw:Typename": "typename",
        # schema namespace, i.e. http://www.isotc211.org/2005/gmd
        "pycsw:Schema": "schema",
        # origin of resource, either 'local', or URL to web service
        "pycsw:MdSource": "mdsource",
        # date of insertion
        "pycsw:InsertDate": "insert_date",  # date of insertion
        # raw XML metadata
        "pycsw:XML": "xml",
        # raw metadata payload, xml to be migrated to this in the future
        "pycsw:Metadata": "metadata",
        # raw metadata payload type, xml as default for now
        "pycsw:MetadataType": "metadata_type",
        # bag of metadata element and attributes ONLY, no XML tages
        "pycsw:AnyText": "anytext",
        "pycsw:Language": "language",
        "pycsw:Title": "title",
        "pycsw:Abstract": "abstract",
        "pycsw:Edition": "edition",
        "pycsw:Keywords": "keywords",
        "pycsw:KeywordType": "keywordstype",
        "pycsw:Format": "format",
        "pycsw:Source": "source",
        "pycsw:Date": "date",
        "pycsw:Modified": "date_modified",
        "pycsw:Type": "type",
        # geometry, specified in OGC WKT
        "pycsw:BoundingBox": "wkt_geometry",
        "pycsw:CRS": "crs",
        "pycsw:AlternateTitle": "title_alternate",
        "pycsw:RevisionDate": "date_revision",
        "pycsw:CreationDate": "date_creation",
        "pycsw:PublicationDate": "date_publication",
        "pycsw:OrganizationName": "organization",
        "pycsw:SecurityConstraints": "securityconstraints",
        "pycsw:ParentIdentifier": "parentidentifier",
        "pycsw:TopicCategory": "topiccategory",
        "pycsw:ResourceLanguage": "resourcelanguage",
        "pycsw:GeographicDescriptionCode": "geodescode",
        "pycsw:Denominator": "denominator",
        "pycsw:DistanceValue": "distancevalue",
        "pycsw:DistanceUOM": "distanceuom",
        "pycsw:TempExtent_begin": "time_begin",
        "pycsw:TempExtent_end": "time_end",
        "pycsw:ServiceType": "servicetype",
        "pycsw:ServiceTypeVersion": "servicetypeversion",
        "pycsw:Operation": "operation",
        "pycsw:CouplingType": "couplingtype",
        "pycsw:OperatesOn": "operateson",
        "pycsw:OperatesOnIdentifier": "operatesonidentifier",
        "pycsw:OperatesOnName": "operatesoname",
        "pycsw:Degree": "degree",
        "pycsw:AccessConstraints": "accessconstraints",
        "pycsw:OtherConstraints": "otherconstraints",
        "pycsw:Classification": "classification",
        "pycsw:ConditionApplyingToAccessAndUse": "conditionapplyingtoaccessanduse",
        "pycsw:Lineage": "lineage",
        "pycsw:ResponsiblePartyRole": "responsiblepartyrole",
        "pycsw:SpecificationTitle": "specificationtitle",
        "pycsw:SpecificationDate": "specificationdate",
        "pycsw:SpecificationDateType": "specificationdatetype",
        "pycsw:Creator": "creator",
        "pycsw:Publisher": "publisher",
        "pycsw:Contributor": "contributor",
        "pycsw:Relation": "relation",
        "pycsw:Platform": "platform",
        "pycsw:Instrument": "instrument",
        "pycsw:SensorType": "sensortype",
        "pycsw:CloudCover": "cloudcover",
        "pycsw:Bands": "bands",
        # links: list of dicts with properties: name, description, protocol, url
        "pycsw:Links": "links",
    },
}
