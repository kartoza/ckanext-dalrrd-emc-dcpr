import typing
import uuid

from . import (
    _CkanBootstrapErrorReport,
)


SAMPLE_ERROR_REPORTS: typing.Final[typing.List[_CkanBootstrapErrorReport]] = [
    _CkanBootstrapErrorReport(
        csi_reference_id=uuid.UUID("f2cdd103-77e2-45dc-b9cf-e374c4a8b870"),
        status="status",
        error_application="Error application",
        error_description="Error description",
        solution_description="Solution description",
        request_date="2022-01-01",
        nsif_moderation_notes="CSI moderation notes",
        nsif_review_additional_documents="CSI review additional documents",
        nsif_moderation_date="2022-01-01",
    ),
    _CkanBootstrapErrorReport(
        csi_reference_id=uuid.UUID("3a401e31-6e96-436a-ae98-dfba12f331d2"),
        status="Another status for the error report",
        error_application="Another error application",
        error_description="Another error description",
        solution_description="Another solution description",
        request_date="2022-01-01",
        nsif_moderation_notes="CSI moderation notes",
        nsif_review_additional_documents="CSI review additional documents",
        nsif_moderation_date="2022-01-01",
    ),
]
