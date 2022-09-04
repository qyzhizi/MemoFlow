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

        mapper.connect('/hello2/{name}',
                       controller=test_controller,
                       action='test2',
                       conditions=dict(method=['GET']))

        mapper.connect('/lzw/{name}',
                       controller=test_controller,
                       action='test_lzw',
                       conditions=dict(method=['GET']))


