import json
# from webob.exc import HTTPBadRequest
# from  webob.exc import WSGIHTTPException
from webob.response import Response

class VisibleException(Exception):
    def __init__(self, detail=None, status=400):
        Exception.__init__(self, detail)
        self.status = status

class VisiblePathException(VisibleException):
    def __init__(self, detail=None, status=400):
        VisibleException.__init__(self, detail, status)

class VisibleResponse(Response):
    def __init__(self, body:str=None, status=None):
        body = json.dumps({'VisibleError': body})
        Response.__init__(self, body=body, status=status)

class ServerErrorResponse(Response):
    def __init__(self, body:str=None, status=None):
        body = json.dumps({'Server Error': body})
        Response.__init__(self, body=body, status=status)