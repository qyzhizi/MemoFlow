#!/usr/bin/env python
# coding=utf-8
from web_dl.common import wsgi
from web_dl.app.diary_log import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        diary_log_controller = controllers.DiaryLog()
        mapper.connect('/diary-log/index.html',
                       controller=diary_log_controller,
                       action='get_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/getlogs',
                       controller=diary_log_controller,
                       action='get_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/addlog',
                       controller=diary_log_controller,
                       action='add_log',
                       conditions=dict(method=['POST']))
        mapper.connect('/diary-log/log.js',
                       controller=diary_log_controller,
                       action='get_js',
                       conditions=dict(method=['GET']))                                             
        mapper.connect('/diary-log/delete_all_log',
                       controller=diary_log_controller,
                       action='delete_all_log',
                       conditions=dict(method=['GET']))        