#!/usr/bin/env python
# coding=utf-8
import logging

from memoflow.core import dependency
from memoflow.conf import CONF

LOG = logging.getLogger(__name__)

INDEX_HTML_PATH = CONF.diary_log_client['index_html_path']
LOG_JS_PATH = CONF.diary_log_client['log_js_path']

@dependency.provider('diary_log_client_api')
class Manager(object):

    def __init__(self):
        pass

    def get_html(self, index_html_path=INDEX_HTML_PATH):
        with open(index_html_path, "r", encoding='UTF-8')as f:
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
    