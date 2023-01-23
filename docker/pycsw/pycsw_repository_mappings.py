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
        "pycsw:SiteURL": "http://localhost:5000/dataset/",  # grap this from a file or a process.
        "pycsw:Language": "language",
        "pycsw:Title": "title",
        "pycsw:DatasetName": "dataset_name",
        "pycsw:DatasetCharacterSet": "dataset_character_set",
        "pycsw:Abstract": "abstract",
        "pycsw:Edition": "edition",
        "pycsw:MetadataStandardName": "metadata_standard",
        "pycsw:MetadataStandardVersion": "metadata_standard_version",
        "pycsw:Keywords": "keywords",
        "pycsw:KeywordType": "keywordstype",
        "pycsw:Format": "format",
        "pycsw:Source": "source",
        "pycsw:Date": "reference_date",
        "pycsw:DateType": "reference_date_type",
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
        "pycsw:SASDITheme": "sasditheme",
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
        "pycsw:Lineage": "dataset_lineage",  # this is not used as a value, but required by pycsw
        "pycsw:LineageStatement": "lineage_statement",
        "pycsw:ContactIndividualName": "contact_individual_name",
        "pycsw:ContactPositionName": "contact_position_name",
        "pycsw:ContactAddressDeliveryPoint": "contact_delivery_point",
        "pycsw:ContactAddressCity": "contact_address_city",
        "pycsw:ContactAddressAdministrativeArea": "contact_address_administrative_area",
        "pycsw:ContactAddressPostalCode": "contact_postal_code",
        "pycsw:ContactAddressElectronicMailAddress": "contact_electronic_mail_address",
        "pycsw:ContactPhone": "contact_phone",
        "pycsw:ContactFacsimile": "contact_facsimile",
        "pycsw:ContactOrganisationalRole": "contact_organisational_role",
        # responsible party
        "pycsw:ContactIndividualName": "contact_individual_name",
        "pycsw:ContactPositionName": "contact_position_name",
        "pycsw:ContactAddressDeliveryPoint": "contact_delivery_point",
        "pycsw:ContactAddressCity": "contact_address_city",
        "pycsw:ContactAddressAdministrativeArea": "contact_address_administrative_area",
        "pycsw:ContactAddressPostalCode": "contact_postal_code",
        "pycsw:ContactAddressElectronicMailAddress": "contact_electronic_mail_address",
        "pycsw:ContactPhone": "contact_phone",
        "pycsw:ContactFacsimile": "contact_facsimile",
        "pycsw:ContactOrganisationalRole": "contact_organisational_role",
        #
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
        "pycsw:BoundingGeoJSON": "bounding_geojson",
        "pycsw:EquivalentScale": "equivalent_scale",
        "pycsw:TemporalExtentPositionBegin": "temporal_position_begin",
        "pycsw:TemporalExtentPositionEnd": "temporal_position_end",
        "pycsw:VerticalExtentMinimum": "minimum_vertical_ex",
        "pycsw:VerticalExtentMaximum": "maximum_vertical_ex",
    },
}
