import functools

from ckan.config.middleware import make_app
from ckan.plugins import toolkit


def provide_request_context(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        app = make_app(toolkit.config)
        with app._wsgi_app.test_request_context() as context:
            result = func(context, *args, **kwargs)
        return result

    return wrapped
