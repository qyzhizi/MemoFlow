#!/usr/bin/env python
# coding=utf-8
from web_dl.core import wsgi
from web_dl.app.test_app import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        test_app_controller = controllers.TestApp()
        mapper.connect('/test_app/hello',
                       controller=test_app_controller,
                       action='test_app_hello',
                       conditions=dict(method=['GET']))





