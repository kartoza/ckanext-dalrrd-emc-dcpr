from ckan.logic.schema import validator_args


@validator_args
def show_dcpr_request_schema(not_missing, not_empty, unicode_safe):
    return {"csi_reference_id": [not_missing, not_empty, unicode_safe]}


@validator_args
def create_dcpr_request_schema(
    ignore_missing,
    not_missing,
    not_empty,
    unicode_safe,
    is_positive_integer,
    isodate,
    convert_group_name_or_id_to_id,
    dcpr_end_date_after_start_date_validator,
):
    return {
        "proposed_project_name": [not_empty, not_missing, unicode_safe],
        "organization_id": [
            not_missing,
            not_empty,
            unicode_safe,
            convert_group_name_or_id_to_id,
        ],
        "additional_project_context": [ignore_missing, unicode_safe],
        "capture_start_date": [
            not_empty,
            isodate,
            dcpr_end_date_after_start_date_validator,
        ],
        "capture_end_date": [not_empty, isodate],
        "cost": [not_missing, not_empty, is_positive_integer],
        "spatial_extent": [ignore_missing, unicode_safe],
        "spatial_resolution": [ignore_missing, unicode_safe],
        "data_capture_urgency": [ignore_missing, unicode_safe],
        "additional_documents": [unicode_safe, ignore_missing],
        "datasets": create_dcpr_request_dataset_schema(),
    }


def create_error_report_schema(
    ignore_missing,
    not_missing,
    not_empty,
    unicode_safe,
):
    return {
        "metadata_record": [
            not_missing,
            not_empty,
            unicode_safe
        ],
        "error_application": [ignore_missing, unicode_safe],
        "error_description": [not_missing, not_empty],
        "solution_description": [ignore_missing, unicode_safe],
        "request_date": [ignore_missing, unicode_safe],
        "nsif_moderation_notes": [ignore_missing, unicode_safe],
        "nsif_review_additional_documents": [ignore_missing, unicode_safe],
        "nsif_moderation_date": [ignore_missing, unicode_safe],
    }


@validator_args
def update_error_report_by_owner_schema(
    ignore_missing,
    not_missing,
    not_empty,
    unicode_safe,
):
    return {
        "metadata_record": [
            not_missing,
            not_empty,
            unicode_safe
        ],
        "error_application": [ignore_missing, unicode_safe],
        "error_description": [not_missing, not_empty],
        "solution_description": [ignore_missing, unicode_safe],
        "request_date": [ignore_missing, unicode_safe],
        "nsif_moderation_notes": [ignore_missing, unicode_safe],
        "nsif_review_additional_documents": [ignore_missing, unicode_safe],
        "nsif_moderation_date": [ignore_missing, unicode_safe],
    }


@validator_args
def update_dcpr_request_by_owner_schema(
    convert_group_name_or_id_to_id,
    ignore_missing,
    isodate,
    is_positive_integer,
    not_missing,
    not_empty,
    unicode_safe,
):
    return {
        "csi_reference_id": [not_missing, not_empty, unicode_safe],
        "proposed_project_name": [ignore_missing, not_empty, unicode_safe],
        "organization_id": [
            ignore_missing,
            not_empty,
            unicode_safe,
            convert_group_name_or_id_to_id,
        ],
        "additional_project_context": [ignore_missing, unicode_safe],
        "capture_start_date": [ignore_missing, not_empty, isodate],
        "capture_end_date": [ignore_missing, not_empty, isodate],
        "cost": [ignore_missing, not_empty, is_positive_integer],
        "spatial_extent": [ignore_missing, unicode_safe],
        "spatial_resolution": [ignore_missing, unicode_safe],
        "data_capture_urgency": [ignore_missing, unicode_safe],
        "additional_documents": [unicode_safe, ignore_missing],
        "datasets": create_dcpr_request_dataset_schema(),
    }


@validator_args
def update_dcpr_request_by_nsif_schema(
    ignore_missing,
    not_empty,
    not_missing,
    unicode_safe,
):
    return {
        "csi_reference_id": [not_missing, not_empty, unicode_safe],
        "nsif_recommendation": [ignore_missing, unicode_safe],
        "nsif_review_notes": [ignore_missing, unicode_safe],
        "nsif_review_additional_documents": [ignore_missing, unicode_safe],
    }


@validator_args
def update_dcpr_request_by_csi_schema(
    ignore_missing,
    not_empty,
    not_missing,
    unicode_safe,
):
    return {
        "csi_reference_id": [not_missing, not_empty, unicode_safe],
        "csi_moderation_notes": [ignore_missing, unicode_safe],
        "csi_review_additional_documents": [ignore_missing, unicode_safe],
    }


@validator_args
def dcpr_request_submit_schema():
    return show_dcpr_request_schema()


@validator_args
def moderate_dcpr_request_schema(
    not_missing,
    not_empty,
    dcpr_moderation_choices_validator,
):
    result = show_dcpr_request_schema()
    result["action"] = [
        not_missing,
        not_empty,
        dcpr_moderation_choices_validator,
    ]
    return result


@validator_args
def delete_dcpr_request_schema():
    return show_dcpr_request_schema()


@validator_args
def create_dcpr_request_dataset_schema(
    ignore,
    boolean_validator,
    ignore_missing,
    unicode_safe,
    not_empty,
    not_missing,
):
    return {
        "dcpr_request_id": [ignore],
        "dataset_id": [ignore],
        "proposed_dataset_title": [not_empty, not_missing, unicode_safe],
        "dataset_purpose": [not_empty, not_missing, unicode_safe],
        "dataset_custodian": [boolean_validator],
        "data_type": [ignore_missing, unicode_safe],
        "proposed_abstract": [ignore_missing, unicode_safe],
        "lineage_statement": [ignore_missing, unicode_safe],
        "associated_attributes": [ignore_missing, unicode_safe],
        "data_usage_restrictions": [ignore_missing, unicode_safe],
        "capture_method": [ignore_missing, unicode_safe],
    }


@validator_args
def claim_reviewer_schema():
    return show_dcpr_request_schema()


@validator_args
def resign_reviewer_schema():
    return show_dcpr_request_schema()
