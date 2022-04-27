from ckan.logic.schema import validator_args


@validator_args
def create_dcpr_request_schema(
    boolean_validator,
    ignore_missing,
    not_missing,
    not_empty,
    unicode_safe,
    is_positive_integer,
    isodate,
    group_id_or_name_exists,
):
    return {
        "proposed_project_name": [not_empty, not_missing, unicode_safe],
        "organization_id": [
            not_empty,
            not_missing,
            group_id_or_name_exists,
        ],
        "additional_project_context": [ignore_missing, unicode_safe],
        "capture_start_date": [not_empty, isodate],
        "capture_end_date": [not_empty, isodate],
        "cost": [not_empty, not_missing, is_positive_integer],
        "spatial_extent": [ignore_missing, unicode_safe],
        "spatial_resolution": [ignore_missing, unicode_safe],
        "data_capture_urgency": [ignore_missing, unicode_safe],
        "additional_information": [ignore_missing, unicode_safe],
        "additional_documents": [unicode_safe, ignore_missing],
        "nsif_review_date": [ignore_missing, unicode_safe],
        "nsif_recommendation": [ignore_missing, unicode_safe],
        "nsif_review_notes": [ignore_missing, unicode_safe],
        "nsif_review_additional_documents": [ignore_missing, unicode_safe],
        "csi_moderation_notes": [ignore_missing, unicode_safe],
        "csi_moderation_additional_documents": [ignore_missing, unicode_safe],
        "csi_moderation_date": [ignore_missing, unicode_safe],
        "dcpr_datasets": create_dcpr_request_dataset_schema(),
        "submission_date": [ignore_missing, isodate],
    }


@validator_args
def create_dcpr_request_dataset_schema(
    ignore_missing,
    unicode_safe,
    not_empty,
    not_missing,
):
    return {
        "proposed_dataset_title": [not_empty, not_missing, unicode_safe],
        "dataset_purpose": [not_empty, not_missing, unicode_safe],
        "dataset_custodian": [ignore_missing, unicode_safe],
        "data_type": [ignore_missing, unicode_safe],
        "proposed_abstract": [ignore_missing, unicode_safe],
        "lineage_statement": [ignore_missing, unicode_safe],
        "associated_attributes": [ignore_missing, unicode_safe],
        "feature_description": [ignore_missing, unicode_safe],
        "data_usage_restrictions": [ignore_missing, unicode_safe],
        "capture_method": [ignore_missing, unicode_safe],
        "capture_method_detail": [ignore_missing, unicode_safe],
    }


@validator_args
def update_dcpr_request_schema():
    return create_dcpr_request_schema()
