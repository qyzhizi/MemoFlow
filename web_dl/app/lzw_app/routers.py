#!/usr/bin/env python
# coding=utf-8
from web_dl.common import wsgi
from web_dl.app.lzw_app import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        lzw_app_controller = controllers.LzwApp()
        mapper.connect('/lzw_app/index.html',
                       controller=lzw_app_controller,
                       action='lzw_app_get_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/lzw_app/style.css',
                       controller=lzw_app_controller,
                       action='lzw_app_get_css',
                       conditions=dict(method=['GET']))



