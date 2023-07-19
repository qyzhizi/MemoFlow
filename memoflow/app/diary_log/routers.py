#!/usr/bin/env python
# coding=utf-8
from memoflow.core import wsgi
from memoflow.app.diary_log import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        diary_log_controller = controllers.DiaryLog()
        mapper.connect('/diary-log/getlogs',
                       controller=diary_log_controller,
                       action='get_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/addlog',
                       controller=diary_log_controller,
                       action='add_log',
                       conditions=dict(method=['POST']))
        mapper.connect('/diary-log/delete_all_log',
                       controller=diary_log_controller,
                       action='delete_all_log',
                       conditions=dict(method=['GET']))        
        mapper.connect('/diary-log/test_flomo',
                       controller=diary_log_controller,
                       action='test_flomo',
                       conditions=dict(method=['GET']))                           
        # review
        mapper.connect('/diary-log/get_review_logs',
                       controller=diary_log_controller,
                       action='get_review_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/delete_all_review_log',
                       controller=diary_log_controller,
                       action='delete_all_review_log',
                       conditions=dict(method=['GET']))
        
        # 粘贴板
        mapper.connect('/diary-log/get_clipboard_logs',
                       controller=diary_log_controller,
                       action='get_clipboard_logs',
                       conditions=dict(method=['GET']))
        mapper.connect('/diary-log/clipboard_addlog',
                       controller=diary_log_controller,
                       action='clipboard_addlog',
                       conditions=dict(method=['POST']))
        
        # get contents from github
        mapper.connect('/diary-log/get_contents_from_github',
                       controller=diary_log_controller,
                       action='get_contents_from_github',
                       conditions=dict(method=['GET']))
        # sync contents from github to db
        mapper.connect('/diary-log/sync-contents-from-github-to-db',
                       controller=diary_log_controller,
                       action='sync_contents_from_github_to_db',
                       conditions=dict(method=['GET']))