#!/usr/bin/env python
# coding=utf-8
from webob.response import Response

from web_dl.common import wsgi
from web_dl.common import dependency


@dependency.requires('test_api')
class Test(wsgi.Application):
    def test(self, req, name):
        test = self.test_api.test
        return Response("hello world %s, %s" % (name, test))

