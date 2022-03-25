import enum
import typing

from ckan.lib import jinja_extensions
from ckan.plugins import toolkit
from flask_babel import gettext as flask_ugettext, ngettext as flask_ungettext
from jinja2 import Environment


class DatasetCreationResult(enum.Enum):
    CREATED = "created"
    NOT_CREATED_ALREADY_EXISTS = "already_exists"


def get_jinja_env():
    jinja_env = Environment(**jinja_extensions.get_jinja_env_options())
    jinja_env.install_gettext_callables(flask_ugettext, flask_ungettext, newstyle=True)
    # custom filters
    jinja_env.policies["ext.i18n.trimmed"] = True
    jinja_env.filters["empty_and_escape"] = jinja_extensions.empty_and_escape
    # jinja_env.filters["ungettext"] = flask_ungettext
    return jinja_env


def create_single_dataset(
    user: typing.Dict, dataset: typing.Dict
) -> DatasetCreationResult:
    create_dataset_action = toolkit.get_action("package_create")
    get_dataset_action = toolkit.get_action("package_show")
    try:
        get_dataset_action(
            context={"user": user["name"]}, data_dict={"id": dataset["name"]}
        )
    except toolkit.ObjectNotFound:
        package_exists = False
    else:
        package_exists = True
    if not package_exists:
        create_dataset_action(context={"user": user["name"]}, data_dict=dataset)
        result = DatasetCreationResult.CREATED
    else:
        result = DatasetCreationResult.NOT_CREATED_ALREADY_EXISTS
    return result


def maybe_create_organization(org_id: str) -> typing.Tuple[typing.Dict, bool]:
    try:
        organization = toolkit.get_action("organization_show")(
            datadict={
                "id": org_id,
                "include_users": True,
                "include_datasets": False,
                "include_dataset_count": False,
                "include_groups": False,
                "include_tags": False,
                "include_followers": False,
            }
        )
        created = False
    except toolkit.ObjectNotFound:
        # org does not exist yet, create it
        user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
        organization = toolkit.get_action("organization_create")(
            context={
                "user": user["name"],
            },
            data_dict={
                "name": org_id,
                "title": org_id,
                "description": "",
            },
        )
        created = True
    return organization, created
