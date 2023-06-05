#!/usr/bin/env python
# coding=utf-8
import os
import openai
import logging

from webob.response import Response

from memocard.core import wsgi
from memocard.core import dependency

LOG = logging.getLogger(__name__)


class TestApp(wsgi.Application):
    def test_app_hello(self, req):

        return "test_app, hello"

 