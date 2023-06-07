import ckan.plugins.toolkit as toolkit
from ckan import model
import logging
from sqlalchemy import select, and_, table, func


logger = logging.getLogger(__name__)


@toolkit.side_effect_free
def stats_list_public_metadata_records_by_date(context, data_dict):
    """
    returns a list of the
    public records based on
    a timespan
    """
    logger.debug("------------ inisde stats list public by date")

    start = data_dict.get("start")
    end = data_dict.get("end")

    toolkit.check_access("stats_public_records_list_auth", context, data_dict)

    q = select(
        [
            model.package_table.c.title,
            model.package_table.c.name,
            model.package_table.c.creator_user_id,
            model.package_table.c.metadata_created,
        ]
    ).where(
        and_(
            model.package_table.c.private == False,
            model.package_table.c.metadata_created >= start,
            model.package_table.c.metadata_created <= end,
            model.package_table.c.state == "active",
        )
    )
    public_packages = model.Session.execute(q).fetchall()
    return public_packages


def stats_list_records_by_location(context, data_dict):
    """
    returns a list of the
    public records based on
    a location
    """
    package_table = table("package")
    package_extra_table = table("package_extra")
    spatial_bounds = data_dict.get("spatial_bounds")
    logger.debug("------------ inisde stats list public by location")
    toolkit.check_access("stats_public_records_list_auth", context, data_dict)
    q = select(
        [
            model.package_table.c.title,
            model.package_table.c.name,
            model.package_table.c.creator_user_id,
            model.package_table.c.metadata_created,
        ],
        from_obj=[
            package_table.join(
                package_extra_table,
                package_table.c.id == package_extra_table.c.package_id,
            )
        ],
    ).where(
        and_(
            model.package_table.c.private == False,
            model.package_table.c.state == "active",
            model.package_extra_table.c.key == "spatial",
            func.ST_WITHIN(model.package_extra_table.c.value, spatial_bounds),
        )
    )

    public_packages = model.Session.execute(q).fetchall()
    return public_packages
