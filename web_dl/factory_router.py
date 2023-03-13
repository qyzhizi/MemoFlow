#!/usr/bin/env python
# coding=utf-8
import functools
import logging as log
import routes
import sys

from web_dl.common import wsgi
import web_dl.app.test_demo.routers as test_demo_routers
import web_dl.app.test_app.routers as test_app_routers
import web_dl.app.lzw_app.routers as lzw_app_routers
import web_dl.app.diary_log.routers as diary_log_routers
import web_dl.app.diary_log_lrx.routers as diary_log_lrx_routers
LOG = log.getLogger(__name__)


def fail_gracefully(f):
    """Log exceptions and aborts."""
    @functools.wraps(f)
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception as e:
            LOG.debug(e, exc_info=True)

            # exception message is printed to all logs
            LOG.critical(e)
            sys.exit(1)

    return wrapper


def warn_local_conf(f):
    @functools.wraps(f)
    def wrapper(*args, **local_conf):
        if local_conf:
            LOG.warning("'local conf' from PasteDeploy INI is being ignored.")
        return f(*args, **local_conf)
    return wrapper


@fail_gracefully
@warn_local_conf
def public_app_factory(global_conf, **local_conf):
    return wsgi.ComposingRouter(routes.Mapper(),
                               [
                                test_demo_routers.Router(),
                                test_app_routers.Router(),
                                lzw_app_routers.Router(),
                                diary_log_routers.Router(),
                                diary_log_lrx_routers.Router()
                               ])

