#!/usr/bin/env python
# coding=utf-8
from memoflow.core import wsgi
from memoflow.client_app.diary_log import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        diary_log_controller = controllers.DiaryLog()
        mapper.connect('/diary-log',
                       controller=diary_log_controller,
                       action='get_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/',
                       controller=diary_log_controller,
                       action='redirect_get_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/index.css',
                       controller=diary_log_controller,
                       action='get_index_css',
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
        mapper.connect('/diary-log/clipboard',
                       controller=diary_log_controller,
                       action='get_clipboard_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/clipboard.js',
                       controller=diary_log_controller,
                       action='get_clipboard_js',
                       conditions=dict(method=['GET']))                                             

        # vector_search
        mapper.connect('/diary-log/vector-search',
                       controller=diary_log_controller,
                       action='get_vector_search_html',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/vector-search.js',
                       controller=diary_log_controller,
                       action='get_vector_search_js',
                       conditions=dict(method=['GET']))
        
        # login
        mapper.connect('/diary-log/login',
                        controller=diary_log_controller,
                        action='get_login_html',
                        conditions=dict(method=['GET']))

        # register
        mapper.connect('/diary-log/register',
                        controller=diary_log_controller,
                        action='get_register_html',
                        conditions=dict(method=['GET']))
        
        mapper.connect('/diary-log/register.js',
                        controller=diary_log_controller,
                        action='get_register_js',
                        conditions=dict(method=['GET']))
        # Settings
        mapper.connect('/diary-log/setting',
                        controller=diary_log_controller,
                        action='get_setting_html',
                        conditions=dict(method=['GET']))
        mapper.connect('/diary-log/setting.js',
                        controller=diary_log_controller,
                        action='get_setting_js',
                        conditions=dict(method=['GET']))
        
        # github-authenticate
        mapper.connect('/diary-log/github-authenticate',
                        controller=diary_log_controller,
                        action='github_authenticate',
                        conditions=dict(method=['GET']))
        # github-authenticate-callback
        mapper.connect('/diary-log/github-authenticate-callback',
                        controller=diary_log_controller,
                        action='github_authenticate_callback',
                        conditions=dict(method=['GET']))
        
        # github-setting-content
        mapper.connect('/diary-log/get-github-setting-content.html',
                       controller=diary_log_controller,
                       action='get_github_setting_content_html',
                       conditions=dict(method=['GET'])
                       )
        # static file
        mapper.connect('/diary-log/static/{file_path:.*}',
                       controller=diary_log_controller,
                       action='serve_static_file',
                       conditions=dict(method=['GET']))
