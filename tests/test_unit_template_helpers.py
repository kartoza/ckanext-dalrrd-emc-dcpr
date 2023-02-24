import json
from unittest import mock

import pytest
from shapely import geometry

from ckan.tests import factories, helpers

from ckan import model

from ckanext.dalrrd_emc_dcpr import helpers as h

pytestmark = pytest.mark.unit

import logging

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "coords, padding, expected_geom",
    [
        pytest.param(
            [
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
                [0, 0],
            ],
            0.1,
            geometry.Polygon(
                (
                    (-0.1, -0.1),
                    (1.1, -0.1),
                    (1.1, 1.1),
                    (-0.1, 1.1),
                    (-0.1, -0.1),
                )
            ),
        ),
        pytest.param(
            [
                [16.4699, -46.9657],
                [37.9777, -46.9657],
                [37.9777, -22.1265],
                [16.4699, -22.1265],
                [16.4699, -46.9657],
            ],
            1,
            geometry.Polygon(
                (
                    (15.4699, -47.9657),
                    (38.9777, -47.9657),
                    (38.9777, -21.1265),
                    (15.4699, -21.1265),
                    (15.4699, -47.9657),
                )
            ),
        ),
    ],
)
def test_pad_geospatial_extent(coords, padding, expected_geom):
    result = h._pad_geospatial_extent(
        {"type": "Polygon", "coordinates": [coords]}, padding
    )
    result_geom = geometry.shape(result)
    print(f"result_geom: {result_geom}")
    assert result_geom.almost_equals(expected_geom, 6)


@pytest.mark.parametrize(
    "coords, padding, expected",
    [
        pytest.param(
            [
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
                [0, 0],
            ],
            None,
            geometry.Polygon(
                (
                    (0, 0),
                    (1, 0),
                    (1, 1),
                    (0, 1),
                    (0, 0),
                )
            ),
        ),
    ],
)
def test_get_default_spatial_search_extent(
    app, ckan_config, monkeypatch, coords, padding, expected
):
    extent = json.dumps({"type": "Polygon", "coordinates": [coords]})
    with app.flask_app.app_context():
        monkeypatch.setitem(
            ckan_config, "ckan.dalrrd_emc_dcpr.default_spatial_search_extent", extent
        )
        result = h.get_default_spatial_search_extent(padding_degrees=padding)
        result_geom = geometry.shape(json.loads(result))
        assert result_geom.almost_equals(expected)


# def test_organization_dataset_count(): # not completed yet
#     """
#     for different users, different
#     counts should show up
#     """

#     # try get the users in local machine first then create them
#     user1,user2 = [None, None]
#     try:
#         query = model.Session.query(model.User).filter(
#             model.User.sysadmin=='f'
#         )
#         result = query.all()
#         user1,user2 = result[0], result[1]
#     except:
#         logger.error("error retrieving users from test database")
#     if user1 is None and user2 is None:
#         user1 = factories.User(name='tester_user1', email='test@user1.com')
#         user2 = factories.User(name='tester_user2', email='test@user2.com')
#     query = model.Session.query(model.User).filter(
#         model.User.sysadmin=='t'
#     )
#     admin = query.all()[0]

#     # try to get the org first and then create it if none
#     # owner_organization = None
#     # try:
#     query = model.Session.query(model.Group).filter(
#         model.Group.name=='new_org_1'
#     )

#     owner_organization = query.all()[0]

#     # except:
#     #     logger.error("error getting the organization by it's name 'new_org_1'")


#     # if owner_organization is None:
#     #     owner_organization = factories.Organization(name="new_org_1")

#     helpers.call_action(
#         "organization_member_create",
#         id=owner_organization.id,
#         username=user1.id,
#         role="member",
#     )

#     data_dict1 = create_package("dataset1", False, owner_organization)
#     data_dict2 = create_package("dataset2", True, owner_organization)
#     data_dict3 = create_package("dataset2", False, owner_organization)

#     for ds in [data_dict1, data_dict2, data_dict3]:
#         helpers.call_action(
#             "package_create",
#             context={"ignore_auth": False, "user": user1},
#             **ds,
#         )


#     count = h.get_org_public_records_count(owner_organization.id)
#     assert count == 2


# def create_package(name, private, owner_organization):
#     data_dict = {
#         "name": name,
#         "private": private,
#         "title": name,
#         "doi": "",
#         "metadata_standard-0-name": "sans1878",
#         "metadata_standard-0-version": "1.1",
#         "notes": f"notes for {name}",
#         "responsible_party-0-individual_name": "individual",
#         "responsible_party-0-position_name": "position",
#         "responsible_party-0-role": "owner",
#         "responsible_party-0-electronic_mail_address": "someone@mail",
#         "responsible_party_contact_info-0-voice": "+27-101-000-000",
#         "responsible_party_contact_info-0-facsimile": "+27-101-000-000",
#         "responsible_party_contact_address-0-delivery_point": "delivery point",
#         "responsible_party_contact_address-0-city": "city",
#         "responsible_party_contact_address-0-administrative_area": "address_area",
#         "responsible_party_contact_address-0-postal_code": "postalcode",
#         "metadata_reference_date_and_stamp-0-reference": "2023-01-13",
#         "metadata_reference_date_and_stamp-0-reference_date_type": "1",
#         "topic_and_sasdi_theme-0-iso_topic_category": "biota",
#         "owner_org": owner_organization.id,
#         "metadata_language_and_character_set-0-dataset_language": "en",
#         "metadata_language_and_character_set-0-metadata_language": "en",
#         "metadata_language_and_character_set-0-dataset_character_set": "utf-8",
#         "metadata_language_and_character_set-0-metadata_character_set": "utf-8",
#         "lineage_statement": f"dataset_lineage statement for {name}",
#         "distribution_format-0-name": "format",
#         "distribution_format-0-version": "1.0",
#         "online_resource-0-name": "name",
#         "online_resource-0-linkeage": "linkage",
#         "online_resource-0-description": "1",
#         "online_resource-0-application_profile": "application_profile",
#         "contact-0-individual_name": "contact",
#         "contact-0-role": "point_of_contact",
#         "contact-0-position_name": "contact",
#         "contact-0-electronic_mail_address": "someone@mail",
#         "contact_information-0-voice": "+27-101-000-000",
#         "contact_information-0-facsimile": "+27-101-000-000",
#         "contact_address-0-delivery_point": "delivery point",
#         "contact_address-0-city": "city",
#         "contact_address-0-administrative_area": "address_area",
#         "contact_address-0-postal_code": "postalcode",
#         "maintainer": "Surname, Name, title.",
#         "spatial": json.dumps(
#             {
#                 "type": "Polygon",
#                 "coordinates": [
#                     [
#                         [10.0, 10.0],
#                         [10.31, 10.0],
#                         [10.31, 10.44],
#                         [10.0, 10.44],
#                         [10.0, 10.0],
#                     ]
#                 ],
#             }
#         ),
#         "spatial_parameters-0-equivalent_scale": "500",
#         "spatial_parameters-0-spatial_representation_type": "001",
#         "spatial_parameters-0-spatial_reference_system": "EPSG:4326",
#         "reference_system_additional_info": "desc",
#         "metadata_reference_date_and_stamp-0-stamp": "2020-01-01",
#         "metadata_reference_date_and_stamp-0-stamp_date_type": "1",
#     }

#     return data_dict
