# import uuid
# import logging
# import json
# import pytest

# from ckan.tests import (
#     factories,
#     helpers,
# )

# from ckan.plugins import toolkit
# from ckan import model, logic

# from sqlalchemy import exc

# logger = logging.getLogger(__name__)

# SAMPLE_ERROR_REPORTS = [
#     {
#         "error_application": "Another error application",
#         "error_description": "Another error description",
#         "solution_description": "Another solution description",
#         "nsif_moderation_notes": "NSIF moderation notes",
#         "nsif_review_additional_documents": "NSIF review additional documents",
#         "nsif_moderation_date": "2022-01-01",
#     },
#     {
#         "status": "Another status for the error report",
#         "error_application": "Another error application",
#         "error_description": "Another error description",
#         "solution_description": "Another solution description",
#         "nsif_moderation_notes": "NSIF moderation notes",
#         "nsif_review_additional_documents": "NSIF review additional documents",
#         "nsif_moderation_date": "2022-01-01",
#     },
# ]

# pytestmark = pytest.mark.integration


# @pytest.mark.parametrize(
#     "name, user_available, user_logged",
#     [
#         pytest.param(
#             "report_1",
#             True,
#             True,
#             id="report-added-successfully",
#         ),
#         pytest.param(
#             "report_2",
#             False,
#             True,
#             marks=pytest.mark.raises(exception=logic.ValidationError),
#             id="report-can-not-be-added-integrity-error",
#         ),
#         pytest.param(
#             "report_3",
#             True,
#             True,
#             id="report-can-be-added-custom-report-id",
#         ),
#     ],
# )
# @pytest.mark.usefixtures(
#     "emc_clean_db", "with_plugins", "with_request_context", "emc_create_sasdi_themes"
# )
# def test_create_error_report(name, user_available, user_logged):
#     user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
#     owner_organization = factories.Organization()

#     package_data_dict = {
#         "name": name,
#         "private": False,
#         "title": name,
#         "metadata_standard_name": "standard name",
#         "metadata_standard_version": "1.0",
#         "notes": f"notes for {name}",
#         "purpose": "purpose",
#         "status": "completed",
#         "metadata_point_of_contact-0-organizational_role": "resource_provider",
#         "reference_date": "2020-01-01",
#         "owner_org": owner_organization.get("id"),
#         "dataset_language": "en",
#         "metadata_language": "en",
#         "dataset_character_set": "utf-8",
#         "lineage-0-level": "001",
#         "lineage-0-lineage_statement": f"lineage statement for {name}",
#         "lineage-0-process_step_description": f"lineage description for {name}",
#         "distribution-0-distributor_contact": "Surname, name, title",
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
#         "equivalent_scale": "500",
#         "spatial_representation_type": "001",
#         "spatial_reference_system": "EPSG:4326",
#         "metadata_date_stamp": "2020-01-01",
#     }

#     package = helpers.call_action(
#         "package_create",
#         context={"ignore_auth": False, "user": user["name"]},
#         **package_data_dict,
#     )
#     package_id = package["id"] if package else None

#     convert_user_name_or_id_to_id = toolkit.get_converter(
#         "convert_user_name_or_id_to_id"
#     )
#     user_id = (
#         convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
#         if user_available
#         else None
#     )

#     for data_dict in SAMPLE_ERROR_REPORTS:
#         data_dict["owner_user"] = user_id
#         data_dict["metadata_record"] = package_id

#         context = {
#             "ignore_auth": not user_logged,
#             "user": user["name"] if user else None,
#         }

#         helpers.call_action(
#             "error_report_create",
#             context=context,
#             **data_dict,
#         )

#     # Remove the test package
#     package_data_dict["id"] = package_id
#     helpers.call_action(
#         "package_delete",
#         context={"ignore_auth": False, "user": user["name"]},
#         **package_data_dict,
#     )


# @pytest.mark.parametrize(
#     "name, user_available, user_logged",
#     [
#         pytest.param(
#             "report_1",
#             True,
#             True,
#             id="report-updated-by-owner",
#         ),
#         pytest.param(
#             "report_2",
#             False,
#             True,
#             marks=pytest.mark.raises(exception=logic.ValidationError),
#             id="report-can-not-be-updated-integrity-error",
#         ),
#     ],
# )
# @pytest.mark.usefixtures(
#     "emc_clean_db", "with_plugins", "with_request_context", "emc_create_sasdi_themes"
# )
# def test_update_error_report(name, user_available, user_logged):
#     user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
#     owner_organization = factories.Organization()

#     package_data_dict = {
#         "name": name,
#         "private": False,
#         "title": name,
#         "metadata_standard_name": "standard name",
#         "metadata_standard_version": "1.0",
#         "notes": f"notes for {name}",
#         "purpose": "purpose",
#         "status": "completed",
#         "metadata_point_of_contact-0-organizational_role": "resource_provider",
#         "reference_date": "2020-01-01",
#         "owner_org": owner_organization.get("id"),
#         "dataset_language": "en",
#         "metadata_language": "en",
#         "dataset_character_set": "utf-8",
#         "lineage-0-level": "001",
#         "lineage-0-lineage_statement": f"lineage statement for {name}",
#         "lineage-0-process_step_description": f"lineage description for {name}",
#         "distribution-0-distributor_contact": "Surname, name, title",
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
#         "equivalent_scale": "500",
#         "spatial_representation_type": "001",
#         "spatial_reference_system": "EPSG:4326",
#         "metadata_date_stamp": "2020-01-01",
#     }

#     package = helpers.call_action(
#         "package_create",
#         context={"ignore_auth": False, "user": user["name"]},
#         **package_data_dict,
#     )
#     package_id = package["id"] if package else None

#     convert_user_name_or_id_to_id = toolkit.get_converter(
#         "convert_user_name_or_id_to_id"
#     )
#     user_id = (
#         convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
#         if user_available
#         else None
#     )

#     for data_dict in SAMPLE_ERROR_REPORTS:
#         data_dict["owner_user"] = user_id
#         data_dict["metadata_record"] = package_id

#         context = {
#             "ignore_auth": not user_logged,
#             "user": user["name"] if user else None,
#         }

#         created_error_report = helpers.call_action(
#             "error_report_create",
#             context=context,
#             **data_dict,
#         )

#         data_dict["csi_reference_id"] = created_error_report.get("csi_reference_id")
#         updated_description = "Updated error report description"
#         data_dict["error_description"] = updated_description

#         error_report = helpers.call_action(
#             "error_report_update_by_owner",
#             context=context,
#             **data_dict,
#         )

#         assert error_report.get("error_description") == updated_description

#     # Remove the test package and the org
#     package_data_dict["id"] = package_id
#     helpers.call_action(
#         "package_delete",
#         context={"ignore_auth": False, "user": user["name"]},
#         **package_data_dict,
#     )


# @pytest.mark.parametrize(
#     "name, user_available, user_logged",
#     [
#         pytest.param(
#             "report_1",
#             True,
#             True,
#             id="report-deleted-by-owner",
#         ),
#         pytest.param(
#             "report_2",
#             False,
#             True,
#             marks=pytest.mark.raises(exception=logic.ValidationError),
#             id="report-can-not-be-deleted-integrity-error",
#         ),
#     ],
# )
# @pytest.mark.usefixtures(
#     "emc_clean_db", "with_plugins", "with_request_context", "emc_create_sasdi_themes"
# )
# def test_delete_error_report(name, user_available, user_logged):
#     user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
#     owner_organization = factories.Organization()

#     package_data_dict = {
#         "name": name,
#         "private": False,
#         "title": name,
#         "metadata_standard_name": "standard name",
#         "metadata_standard_version": "1.0",
#         "notes": f"notes for {name}",
#         "purpose": "purpose",
#         "status": "completed",
#         "metadata_point_of_contact-0-organizational_role": "resource_provider",
#         "reference_date": "2020-01-01",
#         "owner_org": owner_organization.get("id"),
#         "dataset_language": "en",
#         "metadata_language": "en",
#         "dataset_character_set": "utf-8",
#         "lineage-0-level": "001",
#         "lineage-0-lineage_statement": f"lineage statement for {name}",
#         "lineage-0-process_step_description": f"lineage description for {name}",
#         "distribution-0-distributor_contact": "Surname, name, title",
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
#         "equivalent_scale": "500",
#         "spatial_representation_type": "001",
#         "spatial_reference_system": "EPSG:4326",
#         "metadata_date_stamp": "2020-01-01",
#     }

#     package = helpers.call_action(
#         "package_create",
#         context={"ignore_auth": False, "user": user["name"]},
#         **package_data_dict,
#     )
#     package_id = package["id"] if package else None

#     convert_user_name_or_id_to_id = toolkit.get_converter(
#         "convert_user_name_or_id_to_id"
#     )
#     user_id = (
#         convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
#         if user_available
#         else None
#     )

#     for data_dict in SAMPLE_ERROR_REPORTS:
#         data_dict["owner_user"] = user_id
#         data_dict["metadata_record"] = package_id

#         context = {
#             "ignore_auth": not user_logged,
#             "user": user["name"] if user else None,
#         }

#         created_error_report = helpers.call_action(
#             "error_report_create",
#             context=context,
#             **data_dict,
#         )

#         data_dict["csi_reference_id"] = created_error_report.get("csi_reference_id")

#         helpers.call_action(
#             "error_report_delete",
#             context=context,
#             **data_dict,
#         )

#     # Remove the test package
#     package_data_dict["id"] = package_id
#     helpers.call_action(
#         "package_delete",
#         context={"ignore_auth": False, "user": user["name"]},
#         **package_data_dict,
#     )
