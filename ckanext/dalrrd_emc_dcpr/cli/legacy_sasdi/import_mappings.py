"""Mappings to convert from reported metadata to CKAN organizations and categories"""

# map to convert from the reported custodian to the respective CKAN org
import typing

IMPORT_TAG_NAME: typing.Final[str] = "legacy-sasdi-import"
_STAGING_ORG_NAME: typing.Final[str] = "emc_staging"

CUSTODIAN_MAP: typing.Dict[str, typing.Dict] = {
    _STAGING_ORG_NAME: {
        "title": "EMC Staging Organization",
        "description": "This organization is used for importing data",
    },
    "arc": {
        "aliases": [
            "arc",
            "agricultural research council (arc) - livestock business division - range and fo",
        ],
        "title": "Agricultural Research Council",
    },
    "bmr": {
        "aliases": [
            "Copyright 1975, Bureau of Market Research",
            "Copyright 1980, Bureau of Market Research",
            "Copyright 1985, Bureau of Market Research",
            "Copyright 1987, Bureau of Market Research",
        ],
        "title": "Bureau of Market Research",
    },
    "csir": {
        "aliases": [
            "csir",
            "csir, natural resources and the environment",
            "csir built environment",
        ],
        "title": "Council for Scientific and Industrial Research",
    },
    "dws": {
        "aliases": [
            "Department of Water and Sanitation",
        ],
        "title": "Department of Water and Sanitation",
    },
    "ngi": {
        "aliases": [
            "ngi",
            "chief directorate : national geo-spatial information",
        ],
        "title": "Chief Directorate: National Geo-spatial Information",
    },
    "saeon": {
        "aliases": [
            "saeon",
            "south african environmental observation network",
            "saeon metacat",
            "saeon-gen",
            "saeon fynbos node",
            "SAEON Ndlovu node",
            "SAEON Univeristy of the Witwatwersrand",
        ],
        "title": "South African Environmental Observation Network",
    },
    "saiab": {
        "aliases": [
            "SAIAB",
        ],
        "title": "South African Institute of Aquatic Biodiversity",
    },
    "sanbi": {
        "aliases": [
            "sanbi",
            "south african national biodiversity institite",
        ],
        "title": "South African National Biodiversity Institute",
    },
    "sanparks": {
        "aliases": [
            "SANPaks",
            "SANParks",
            "SANParks, South Africa",
            "SANParks,South Africa",
            "SANParks South Africa",
        ],
        "title": "South African National Parks",
    },
    "sansa": {
        "aliases": ["SANSA"],
        "title": "South African National Space Agency",
    },
    "ssa": {
        "aliases": [
            "Statistics South Africa",
            "Copyright, Statistics South Africa",
            "(c) Statistics South Africa",
            "(c) 1985, Statistics South Africa",
            "Copyright 2000, Statistics South Africa",
            "Copyright 2003, Statistics South Africa",
            "Copyright 2004, Statistics South Africa",
            "Copyright 2006-2010, Statistics South Africa",
            "Copyright 2007-2010, Statistics South Africa",
            "Copyright 2008, Statistics South Africa",
            "Copyright 2008, Statistics South Africa.",
            "Copyright 2009, Statistics South Africa",
            "(c) 2010 , Statistics South Africa",
            "Copyright 2010, Statistics South Africa",
            "(c) 2011 , Statistics South Africa",
            "Copyright 2011, Statistics South Africa",
            "Statistics South Africa, 2012",
        ],
        "title": "Statistics South Africa",
    },
    "saws": {
        "aliases": ["saws", "south african weather service"],
        "title": "South African Weather Service",
    },
    "wrc": {
        "aliases": ["Water Research Commission"],
        "title": "Water Research Commission",
    },
}


def get_owner_org(original_value: str) -> str:
    result = None
    for org_name, org_info in CUSTODIAN_MAP.items():
        for alias in org_info.get("aliases", []):
            if alias.lower() in original_value.lower():
                result = org_name
                break
        if result is not None:
            break
    else:
        result = _STAGING_ORG_NAME
    return result
