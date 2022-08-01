#!/usr/bin/env python
# coding=utf-8
from web_dl.common import wsgi
from web_dl.app.test_demo import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        test_controller = controllers.Test()
        mapper.connect('/hello/{name}',
                       controller=test_controller,
                       action='test',
                       conditions=dict(method=['GET']))

