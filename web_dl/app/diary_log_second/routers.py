#!/usr/bin/env python
# coding=utf-8
from web_dl.common import wsgi
from web_dl.app.diary_log_second import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        diary_log_second_controller = controllers.DiaryLog()
        mapper.connect('/diary-log-second/index.html',
                       controller=diary_log_second_controller,
                       action='get_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log-second/getlogs',
                       controller=diary_log_second_controller,
                       action='get_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log-second/addlog',
                       controller=diary_log_second_controller,
                       action='add_log',
                       conditions=dict(method=['POST']))
        mapper.connect('/diary-log-second/log.js',
                       controller=diary_log_second_controller,
                       action='get_js',
                       conditions=dict(method=['GET']))                                             
        mapper.connect('/diary-log-second/delete_all_log',
                       controller=diary_log_second_controller,
                       action='delete_all_log',
                       conditions=dict(method=['GET']))        
        mapper.connect('/diary-log-second/test_flomo',
                       controller=diary_log_second_controller,
                       action='test_flomo',
                       conditions=dict(method=['GET']))        