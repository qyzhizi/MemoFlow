#!/usr/bin/env python
# coding=utf-8
import os
import logging

from webob import Request
from webob import Response
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

    def get_content_type(self, file_path):
        """
        根据文件路径获取对应的Content-type。

        :param file_path: 文件路径。
        :return: 对应的Content-type。
        """
        extension = os.path.splitext(file_path)[1]
        if extension == '.html':
            return 'text/html'
        elif extension == '.css':
            return 'text/css'
        elif extension == '.js':
            return 'application/javascript'
        elif extension == '.png':
            return 'image/png'        
        else:
            return 'text/plain'  # 默认为纯文本类型
    
    def response_decorator(func):
        def wrapper(self, *args, **kwargs):
            # 调用原始函数，这里假设原始函数返回文件内容
            file_content = func(self, *args, **kwargs)
            
            # 获取文件路径，这里假设它是第一个位置参数或者名为log_js_path的关键字参数
            if args:
                # 获取文件路径，这里它是第一个位置参数
                file_path = args[0]
            elif kwargs and len(kwargs.keys()) == 1:
                # file_path = kwargs[kwargs.keys()[0]]
                file_path = kwargs[next(iter(kwargs))]
            else:
                return file_content
                
            # 获取内容类型
            content_type = self.get_content_type(file_path)
            # 假设 file_content 是您的文本数据
            bytes_content = file_content.encode('utf-8')
            response = Response(body=bytes_content, content_type=content_type)
            # 创建响应对象
            # response = Response(body=file_content, content_type=content_type)
            
            return response
        return wrapper

    @response_decorator
    def get_html(self, index_html_path=INDEX_HTML_PATH):
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    @response_decorator
    def get_index_css(self, index_css_path=INDEX_CSS_PATH):
        with open(index_css_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    @response_decorator
    def get_register_html(self, register_html_path=REGISTER_HTML_PATH):
        with open(register_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    @response_decorator
    def get_register_js(self, register_js_path=REGISTER_JS_PATH):
        with open(register_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    @response_decorator
    def get_login_html(self, login_html_path=LOGIN_HTML_PATH):
        with open(login_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    @response_decorator
    def get_js(self, log_js_path=LOG_JS_PATH):
        with open(log_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        

    # review provider
    @response_decorator
    def get_review_html(self, review_index_html_path):
        with open(review_index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    @response_decorator
    def get_review_js(self, review_js_path):
        with open(review_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    # clipboard
    @response_decorator
    def get_clipboard_html(self, clipboard_html_path):
        with open(clipboard_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    @response_decorator
    def get_clipboard_js(self, clipboard_js_path):
        with open(clipboard_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    # vector_search
    @response_decorator
    def get_vector_search_html(self, index_html_path):
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    @response_decorator
    def get_vector_search_js(self, js_path):
        with open(js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    # Settings
    @response_decorator
    def get_setting_html(self, setting_html_path):
        with open(setting_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    @response_decorator
    def get_setting_js(self, setting_js_path):
        with open(setting_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    @response_decorator
    def github_setting_content_html_path(
            self, github_setting_content_html_path):
        with open(
            github_setting_content_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    