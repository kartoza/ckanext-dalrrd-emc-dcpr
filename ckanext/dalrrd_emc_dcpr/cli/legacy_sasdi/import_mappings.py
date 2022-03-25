"""Mappings to convert from reported metadata to CKAN organizations and categories"""

# map to convert from the reported custodian to the respective CKAN org
import typing

CUSTODIAN_MAP = {
    "ARC": [
        "arc",
        "agricultural research council (arc) - livestock business division - range and fo",
    ],
    "BMR": [
        "Copyright 1975, Bureau of Market Research",
        "Copyright 1980, Bureau of Market Research",
        "Copyright 1985, Bureau of Market Research",
        "Copyright 1987, Bureau of Market Research",
    ],
    "CSIR": [
        "csir",
        "csir, natural resources and the environment",
        "csir built environment",
    ],
    "DWS": [
        "Department of Water and Sanitation",
    ],
    "NGI": [
        "ngi",
        "chief directorate : national geo-spatial information",
    ],
    "SAEON": [
        "saeon",
        "south african environmental observation network",
        "saeon metacat",
        "saeon-gen",
        "saeon fynbos node",
        "SAEON Ndlovu node",
        "SAEON Univeristy of the Witwatwersrand",
    ],
    "SAIAB": [
        "SAIAB",
    ],
    "SANBI": [
        "sanbi",
        "south african national biodiversity institite",
    ],
    "SANPARKS": [
        "SANPaks",
        "SANParks",
        "SANParks, South Africa",
        "SANParks,South Africa",
        "SANParks South Africa",
    ],
    "SANSA": ["SANSA"],
    "SSA": [
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
    "SAWS": ["saws", "south african weather service"],
    "WRC": ["Water Research Commission"],
}


def get_owner_org(original_value: str) -> typing.Optional[str]:
    result = None
    for name, aliases in CUSTODIAN_MAP.items():
        for alias in aliases:
            if alias.lower() in original_value.lower():
                result = name
                break
        if result is not None:
            break
    return result
