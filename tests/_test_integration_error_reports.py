import uuid
import pytest

from ckan.tests import (
    factories,
    helpers,
)

from ckan.plugins import toolkit
from ckan import model, logic
from sqlalchemy import exc

from ckanext.dalrrd_emc_dcpr.cli._sample_dcpr_error_reports import SAMPLE_ERROR_REPORTS

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "name, user_available, user_logged",
    [
        pytest.param(
            "report_1",
            True,
            True,
            id="request-added-successfully",
        ),
        pytest.param(
            "report_2",
            False,
            True,
            marks=pytest.mark.raises(exception=exc.IntegrityError),
            id="report-can-not-be-added-integrity-error",
        ),
        pytest.param(
            "report_3",
            True,
            True,
            id="report-can-be-added-custom-report-id",
        ),
    ],
)
def test_create_dcpr_report(name, user_available, user_logged):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})

    package = model.Session.query(model.Package).first()
    package_id = package.id if package else None

    convert_user_name_or_id_to_id = toolkit.get_converter(
        "convert_user_name_or_id_to_id"
    )
    user_id = (
        convert_user_name_or_id_to_id(user["name"], {"session": model.Session})
        if user_available
        else None
    )

    for report in SAMPLE_ERROR_REPORTS:
        data_dict = {
            "csi_reference_id": uuid.uuid4(),
            "owner_user": user_id,
            "csi_reviewer": user_id,
            "metadata_record": package_id,
            "notification_targets": [{"user_id": user_id, "group_id": None}],
            "status": report.status,
            "error_application": report.error_application,
            "error_description": report.error_description,
            "solution_description": report.solution_description,
            "request_date": report.request_date,
            "nsif_moderation_notes": report.csi_moderation_notes,
            "nsif_review_additional_documents": report.csi_review_additional_documents,
            "nsif_moderation_date": report.csi_moderation_date,
        }

        context = {"ignore_auth": not user_logged, "user": user["name"]}

        helpers.call_action(
            "error_report_create",
            context=context,
            **data_dict,
        )
