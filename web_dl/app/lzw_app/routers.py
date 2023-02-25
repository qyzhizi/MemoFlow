#!/usr/bin/env python
# coding=utf-8
from web_dl.common import wsgi
from web_dl.app.lzw_app import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        lzw_app_controller = controllers.LzwApp()
        mapper.connect('/lzw_app/hello',
                       controller=lzw_app_controller,
                       action='lzw_app_hello',
                       conditions=dict(method=['GET']))



