from logging import getLogger

log = getLogger(__name__)

from sqlalchemy import orm, types, Column, Table, ForeignKey

from ckan.model import core, domain_object, meta

__all__ = ["RequestDataset", "request_dataset"]

request_dataset_table = None


class RequestDataset(domain_object.DomainObject):
    pass


def define_table():
    global request_dataset_table

    request_dataset_table = Table(
        "request_dataset",
        meta.metadata,
        Column("request_id", ForeignKey("request.csi_reference_id"), primary_key=True),
        Column("dataset_custodian", types.Boolean, default=False),
        Column("data_type", types.UnicodeText),
        Column("purposed_dataset_title", types.UnicodeText),
        Column("purposed_abstract", types.UnicodeText),
        Column("dataset_purpose", types.UnicodeText),
        Column("lineage_statement", types.UnicodeText),
        Column("associated_attributes", types.UnicodeText),
        Column("feature_description", types.UnicodeText),
        Column("data_usage_restrictions", types.UnicodeText),
        Column("capture_method", types.UnicodeText),
        Column("capture_method_detail", types.UnicodeText),
    )
    meta.mapper(RequestDataset, request_dataset_table)


def create_table():
    if request_dataset_table is not None:
        request_dataset_table.create()
