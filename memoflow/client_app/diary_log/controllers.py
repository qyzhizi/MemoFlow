#!/usr/bin/env python
# coding=utf-8
from datetime import timezone
from datetime import datetime
import logging
import os
from webob import Response
from webob.exc import HTTPFound

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

SETTINGS_HTML_PATH = CONF.diary_log_client['setting_html_path']
SETTINGS_JS_PATH = CONF.diary_log_client['setting_js_path']
GITHUB_SETTING_CONTENT_HTML_PATH = CONF.diary_log_client[
    'github_setting_content_html_path']
STATIC_FOLDER = CONF.diary_log_client[
    'static_path']

#clipboard
CLIPBOARD_HTML_PATH = CONF.diary_log_client['clipboard_html_path']
CLIPBOARD_JS_PATH = CONF.diary_log_client['clipboard_js_path']

INDEX_CSS_PATH = CONF.diary_log_client['index_css_path']
REGISTER_HTML_PATH = CONF.diary_log_client['register_html_path']
REGISTER_JS_PATH = CONF.diary_log_client['register_js_path']
LOGIN_HTML_PATH = CONF.diary_log_client['login_html_path']


@dependency.requires('diary_log_client_api')
class DiaryLog(wsgi.Application):
    def get_login_html(self, req):
        return self.diary_log_client_api.get_login_html(login_html_path=LOGIN_HTML_PATH)

    # register
    def get_register_html(self, req):
        return self.diary_log_client_api.get_register_html(register_html_path=REGISTER_HTML_PATH)

    def get_register_js(self, req):
        return self.diary_log_client_api.get_register_js(register_js_path=REGISTER_JS_PATH)

    def get_html(self, req):
        return self.diary_log_client_api.get_html(index_html_path=INDEX_HTML_PATH)

    def redirect_get_html(self, req):
        response = HTTPFound(location='/v1/diary-log')
        return response

    def get_index_css(self, req):
        LOG.info("get index css file")
        return self.diary_log_client_api.get_index_css(index_css_path=INDEX_CSS_PATH)

    def get_js(self, req):
        return self.diary_log_client_api.get_js(log_js_path=LOG_JS_PATH)

    # review
    def get_review_html(self, req):
        return self.diary_log_client_api.get_review_html(
            review_index_html_path=REVIEW_INDEX_HTML_PATH)

    def get_review_js(self, req):
        return self.diary_log_client_api.get_review_js(
            review_js_path=REVIEW_JS_PATH)

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

    # Settings
    def get_setting_html(self, req):
        return self.diary_log_client_api.get_setting_html(
            setting_html_path=SETTINGS_HTML_PATH)

    def get_setting_js(self, req):
        return self.diary_log_client_api.get_setting_js(
            setting_js_path=SETTINGS_JS_PATH)

    def get_github_setting_content_html(self, req):
        return self.diary_log_client_api.get_github_setting_content_html(
            github_setting_content_html_path=GITHUB_SETTING_CONTENT_HTML_PATH)

    # def get_content_type(self, file_path):
    #     """
    #     根据文件路径获取对应的Content-type。

    #     :param file_path: 文件路径。
    #     :return: 对应的Content-type。
    #     """
    #     extension = os.path.splitext(file_path)[1]
    #     if extension == '.html':
    #         return 'text/html'
    #     elif extension == '.css':
    #         return 'text/css'
    #     elif extension == '.js':
    #         return 'application/javascript'
    #     else:
    #         return 'text/plain'  # 默认为纯文本类型

    def serve_static_file(self, req, file_path):

        # 构建完整的文件路径
        full_file_path = os.path.join(STATIC_FOLDER, file_path.lstrip('/'))
        last_modified = datetime.fromtimestamp(
            os.path.getmtime(full_file_path),
            tz=timezone.utc).replace(microsecond=0)
        response = Response()
        # Set Cache-Control header to cache the resource for 1 hour
        # response.cache_control = 'public, max-age=3600'        
        # 设置不缓存, 强制每次都验证, 与 if_modified_since 配合使用
        response.headers["Cache-Control"] = "no-cache"
        if req.if_modified_since and req.if_modified_since >= last_modified:
            # 资源未修改，返回304状态码，if-modified-since 是求头中的时间，last_modified是文件最后修改时间
            response.status = '304 Not Modified'
        else:
            content_type = 'text/plain'
            # 检查请求的路径是否指向一个静态文件
            if os.path.isfile(full_file_path):
                # 根据文件后缀名设置相应的Content-type
                content_type = self.diary_log_client_api.get_content_type(
                    full_file_path)
            try:
                # 读取文件内容
                with open(full_file_path, 'rb') as file:
                    file_content = file.read()
                    response.body = file_content
                    response.last_modified = last_modified
                    response.content_type = content_type
            except FileNotFoundError:
                # 文件不存在，返回404
                response.body = "File not found"
                response.status = '404'
            except Exception as e:
                # 其他错误，返回500
                response.body = "Internal Server Error"
                response.status = '500'                
        return response
