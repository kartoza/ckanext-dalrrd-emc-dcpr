from ckan.lib import jinja_extensions
from flask_babel import gettext as flask_ugettext, ngettext as flask_ungettext
from jinja2 import Environment


def get_jinja_env():
    jinja_env = Environment(**jinja_extensions.get_jinja_env_options())
    jinja_env.install_gettext_callables(flask_ugettext, flask_ungettext, newstyle=True)
    # custom filters
    jinja_env.policies["ext.i18n.trimmed"] = True
    jinja_env.filters["empty_and_escape"] = jinja_extensions.empty_and_escape
    # jinja_env.filters["ungettext"] = flask_ungettext
    return jinja_env
