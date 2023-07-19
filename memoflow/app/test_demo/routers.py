#!/usr/bin/env python
# coding=utf-8
from memoflow.core import wsgi
from memoflow.app.test_demo import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        test_controller = controllers.Test()
        mapper.connect('/hello/{name}',
                       controller=test_controller,
                       action='test',
                       conditions=dict(method=['GET']))

        mapper.connect('/chatgpt/{question}',
                       controller=test_controller,
                       action='test_chatgpt',
                       conditions=dict(method=['GET']))

        mapper.connect('/get-html',
                        controller=test_controller,
                        action='get_html',
                        conditions=dict(method=['GET']))

        mapper.connect('/add_diary',
                        controller=test_controller,
                        action='add_diary',
                        conditions=dict(method=['POST']))


