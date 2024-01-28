#!/usr/bin/env python
# coding=utf-8
import logging

from memoflow.conf import CONF
from memoflow.core import wsgi
from memoflow.core import dependency

LOG = logging.getLogger(__name__)

INDEX_HTML_PATH = CONF.diary_log_client['index_html_path']
REVIEW_INDEX_HTML_PATH = CONF.diary_log_client['review_index_html_path']
VECTOR_SEARCH_HTML_PATH = CONF.diary_log_client['vector_search_html_path']
LOG_JS_PATH = CONF.diary_log_client['log_js_path']
REVIEW_JS_PATH = CONF.diary_log_client['review_js_path']
VECTOR_SEARCH_JS_PATH = CONF.diary_log_client['vector_search_js_path']

#clipboard
CLIPBOARD_HTML_PATH = CONF.diary_log_client['clipboard_html_path']
CLIPBOARD_JS_PATH = CONF.diary_log_client['clipboard_js_path']

@dependency.requires('diary_log_client_api')
class DiaryLog(wsgi.Application):
    def get_login_html(self, req):
        return self.diary_log_client_api.get_login_html()

    def get_html(self, req):
        return self.diary_log_client_api.get_html()

    def get_js(self, req):
        return self.diary_log_client_api.get_js()

    # review
    def get_review_html(self, req):
        return self.diary_log_client_api.get_review_html(
            review_index_html_path=REVIEW_INDEX_HTML_PATH)

    def get_review_js(self, req):
        return self.diary_log_client_api.get_review_js(review_js_path=REVIEW_JS_PATH)

    # clipboard
    def get_clipboard_html(self, req):
        return self.diary_log_client_api.get_clipboard_html(
            clipboard_html_path=CLIPBOARD_HTML_PATH)
    
    def get_clipboard_js(self, req):
        return self.diary_log_client_api.get_clipboard_js(
            clipboard_js_path=CLIPBOARD_JS_PATH)
    
    # vector_search
    def get_vector_search_html(self, req):
        return self.diary_log_client_api.get_vector_search_html(
            index_html_path=VECTOR_SEARCH_HTML_PATH)
    
    def get_vector_search_js(self, req):
        return self.diary_log_client_api.get_vector_search_js(
            js_path=VECTOR_SEARCH_JS_PATH)

