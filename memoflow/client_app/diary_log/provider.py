#!/usr/bin/env python
# coding=utf-8
import logging

from webob import Request
import requests
import json
from memoflow.api.github_api import GitHupApi

from memoflow.core import dependency
from memoflow.conf import CONF

LOG = logging.getLogger(__name__)

INDEX_HTML_PATH = CONF.diary_log_client['index_html_path']
INDEX_CSS_PATH = CONF.diary_log_client['index_css_path']
REGISTER_HTML_PATH = CONF.diary_log_client['register_html_path']
REGISTER_JS_PATH = CONF.diary_log_client['register_js_path']
LOGIN_HTML_PATH = CONF.diary_log_client['login_html_path']
LOG_JS_PATH = CONF.diary_log_client['log_js_path']

@dependency.provider('diary_log_client_api')
class Manager(object):

    def __init__(self):
        pass

    def get_html(self, index_html_path=INDEX_HTML_PATH):
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    def get_index_css(self, index_css_path=INDEX_CSS_PATH):
        with open(index_css_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    def get_register_html(self, register_html_path=REGISTER_HTML_PATH):
        with open(register_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_register_js(self, register_js_path=REGISTER_JS_PATH):
        with open(register_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_login_html(self, login_html_path=LOGIN_HTML_PATH):
        with open(login_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_js(self, log_js_path=LOG_JS_PATH):
        with open(log_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        

    # review provider
    def get_review_html(self, review_index_html_path):
        with open(review_index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    def get_review_js(self, review_js_path):
        with open(review_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    # clipboard
    def get_clipboard_html(self, clipboard_html_path):
        with open(clipboard_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    def get_clipboard_js(self, clipboard_js_path):
        with open(clipboard_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    # vector_search
    def get_vector_search_html(self, index_html_path):
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_vector_search_js(self, js_path):
        with open(js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    # Settings
    def get_setting_html(self, setting_html_path):
        with open(setting_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    def get_setting_js(self, setting_js_path):
        with open(setting_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    