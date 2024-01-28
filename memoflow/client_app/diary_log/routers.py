#!/usr/bin/env python
# coding=utf-8
from memoflow.core import wsgi
from memoflow.client_app.diary_log import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        diary_log_controller = controllers.DiaryLog()
        mapper.connect('/diary-log/index.html',
                       controller=diary_log_controller,
                       action='get_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/log.js',
                       controller=diary_log_controller,
                       action='get_js',
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
        
        # 粘贴板
        mapper.connect('/diary-log/clipboard.html',
                       controller=diary_log_controller,
                       action='get_clipboard_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/clipboard.js',
                       controller=diary_log_controller,
                       action='get_clipboard_js',
                       conditions=dict(method=['GET']))                                             

        # vector_search
        mapper.connect('/diary-log/vector-search.html',
                       controller=diary_log_controller,
                       action='get_vector_search_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/vector-search.js',
                       controller=diary_log_controller,
                       action='get_vector_search_js',
                       conditions=dict(method=['GET']))
        
        # login
        mapper.connect('/diary-log/login.html',
                        controller=diary_log_controller,
                        action='get_login_html',
                        conditions=dict(method=['GET']))
