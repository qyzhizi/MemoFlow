#!/usr/bin/env python
# coding=utf-8
from memocard.core import wsgi
from memocard.app.diary_log import controllers

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
        mapper.connect('/diary-log/test_flomo',
                       controller=diary_log_controller,
                       action='test_flomo',
                       conditions=dict(method=['GET']))                           
        # review
        mapper.connect('/diary-log/review',
                       controller=diary_log_controller,
                       action='get_review_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/review.js',
                       controller=diary_log_controller,
                       action='get_review_js',
                       conditions=dict(method=['GET']))                                             
        mapper.connect('/diary-log/get_review_logs',
                       controller=diary_log_controller,
                       action='get_review_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/delete_all_review_log',
                       controller=diary_log_controller,
                       action='delete_all_review_log',
                       conditions=dict(method=['GET']))
        
        # 粘贴板
        mapper.connect('/diary-log/clipboard.html',
                       controller=diary_log_controller,
                       action='get_clipboard_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/clipboard.js',
                       controller=diary_log_controller,
                       action='get_clipboard_js',
                       conditions=dict(method=['GET']))                                             
        mapper.connect('/diary-log/get_clipboard_logs',
                       controller=diary_log_controller,
                       action='get_clipboard_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/clipboard_addlog',
                       controller=diary_log_controller,
                       action='clipboard_addlog',
                       conditions=dict(method=['POST']))