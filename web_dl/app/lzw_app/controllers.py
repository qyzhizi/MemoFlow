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
    def lzw_app_hello(self, req):
        LOG.info("lzw_app, hello")
        return "lzw_app, hello"

 