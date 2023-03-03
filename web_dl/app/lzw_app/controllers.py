#!/usr/bin/env python
# coding=utf-8
import os
import openai
import logging

from webob.response import Response

from web_dl.common import wsgi
from web_dl.common import dependency

LOG = logging.getLogger(__name__)


class LzwApp(wsgi.Application):
    def lzw_app_get_html(self, req):
        LOG.info("lzw_app, get_html")
        with open("/root/git_rep/dl/web_dl/web_dl/app/lzw_app/data/index.html", "r", encoding='UTF-8')as f:
            res = f.read()
            # LOG.info(res)
        return res

    def lzw_app_get_css(self, req):
        
        with open("/root/git_rep/dl/web_dl/web_dl/app/lzw_app/data/style.css", "r", encoding='UTF-8')as f:
            res = f.read()
            # LOG.info(res)
        return res