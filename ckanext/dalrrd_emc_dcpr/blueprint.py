from builtins import str
import json
from flask import Blueprint, request

import ckan.plugins.toolkit as t
import ckan.lib.helpers as helpers
from jinja2.exceptions import TemplateNotFound

from ckanext.request.request_registry import Report
from ckanext.request.lib import make_csv_from_dicts, ensure_data_is_dicts, anonymise_user_names

import logging
log = logging.getLogger(__name__)

c = t.c

request = Blueprint(u'request', __name__)


def index():
    try:
        requests = t.get_action('request_list')({}, {})
    except t.NotAuthorized:
        t.abort(401)

    return t.render('dcpr/index.html', extra_vars={'requests': requests})


request.add_url_rule(u'/request', view_func=index)


def get_blueprints():
    return [request]
