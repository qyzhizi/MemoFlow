#!/usr/bin/env python
# coding=utf-8
from webob.response import Response

from web_dl.common import wsgi
class Test(wsgi.Application):
    def test(self, req, name):
        return Response("hello world %s" % name)

