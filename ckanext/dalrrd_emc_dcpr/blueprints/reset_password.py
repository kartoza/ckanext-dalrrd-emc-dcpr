import logging

from ckan.common import config
from ckan.common import asbool
from six import text_type

import ckan.lib.base as base
import ckan.model as model
import ckan.lib.helpers as h
import ckan.authz as authz
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.captcha as captcha
import ckan.lib.mailer as mailer
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.authenticator as authenticator
import ckan.plugins as p

from ckan.common import _, c

from flask import Blueprint, request

log = logging.getLogger(__name__)


abort = base.abort
render = base.render

check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
UsernamePasswordError = logic.UsernamePasswordError

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten

reset_blueprint = Blueprint(
    "validator", __name__, template_folder="templates", url_prefix="/password_reset"
)

def _lowercase(obj):
    """ Make dictionary lowercase """
    if isinstance(obj, dict):
        return {k.lower():_lowercase(v) for k, v in obj.items()}
    elif isinstance(obj, (list, set, tuple)):
        t = type(obj)
        return t(_lowercase(o) for o in obj)
    elif isinstance(obj, str):
        return obj.lower()
    else:
        return obj

@reset_blueprint.route("/", methods = ['POST', 'GET'])
def request_reset():
    context = {'model': model, 'session': model.Session, 'user': c.user,
                'auth_user_obj': c.userobj}
    data_dict = {'id': request.form.get('user')}
    log.debug("sent from blueprint")
    try:
        check_access('request_reset', context)
    except NotAuthorized:
        abort(403, _('Unauthorized to request reset password.'))

    users = _lowercase(logic.get_action('user_list')(context, {}))
    log.info(f"USERS {users}")

    if request.method == 'POST':
        id = request.form.get('user')
        if id in (None, u''):
            h.flash_error(_(u'Email is required'))
            return h.redirect_to(u'/user/reset')
        context = {'model': model,
                    'user': c.user,
                    u'ignore_auth': True}
        user_objs = []

        if u'@' not in id:
            try:
                user_dict = get_action('user_show')(context, {'id': id})
                user_objs.append(context['user_obj'])
            except NotFound:
                try:
                    user_dict = get_action('user_show')(context, {'id': id.lower()})
                    user_objs.append(context['user_obj'])
                except NotFound:
                    try:
                        user_dict = get_action('user_show')(context, {'id': id.capitalize()})
                        user_objs.append(context['user_obj'])
                    except NotFound:
                        log.info("USER NOT FOUND EXCEPT")
                        pass
        else:
            user_list = logic.get_action(u'user_list')(context, {
                u'email': id
            })
            if not user_list:
                user_list = logic.get_action(u'user_list')(context, {
                u'email': id.lower()})
            if not user_list:
                user_list = logic.get_action(u'user_list')(context, {
                u'email': id.capitalize()})
            if user_list:
                # send reset emails for *all* user accounts with this email
                # (otherwise we'd have to silently fail - we can't tell the
                # user, as that would reveal the existence of accounts with
                # this email address)
                for user_dict in user_list:
                    logic.get_action(u'user_show')(
                        context, {u'id': user_dict[u'id']})
                    user_objs.append(context[u'user_obj'])
                

        if not user_objs:
            log.info("USER NOT FOUND IF STATEMENT")
            log.info(u'User requested reset link for unknown user: {}'
                        .format(id))

        for user_obj in user_objs:
            log.info(u'Emailing reset link to user: {}'
                        .format(user_obj.name))
            try:
                mailer.send_reset_link(user_obj)
            except mailer.MailerException as e:
                h.flash_error(
                    _(u'Error sending the email. Try again later '
                        'or contact an administrator for help')
                )
                log.exception(e)
                return h.redirect_to(u'/')
        # always tell the user it succeeded, because otherwise we reveal
        # which accounts exist or not
        h.flash_success(
            _(u'A reset link has been emailed to you '
                '(unless the account specified does not exist)'))
        return h.redirect_to(u'/')
    return render('user/request_reset.html')