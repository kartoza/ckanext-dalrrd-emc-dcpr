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
            id="report-added-successfully",
        ),
        pytest.param(
            "report_2",
            False,
            True,
            marks=pytest.mark.raises(exception=logic.ValidationError),
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
def test_create_error_report(name, user_available, user_logged):
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
            "metadata_record": package_id if user_available else None,
            "status": report.status,
            "error_application": report.error_application,
            "error_description": report.error_description,
            "solution_description": report.solution_description,
        }

        context = {
            "ignore_auth": not user_logged,
            "user": user["name"] if user else None,
        }

        helpers.call_action(
            "error_report_create",
            context=context,
            **data_dict,
        )
