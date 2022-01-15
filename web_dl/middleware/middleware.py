# -*-coding:utf-8 -*-
import abc
import webob.dec


class Middleware(object):

    def __init__(self, application):
        self.application = application

    @abc.abstractmethod
    def process_request(self, request):
        pass

    def process_response(self, response):
        return response

    @webob.dec.wsgify
    def __call__(self, req):
        """ 过滤器，process_request在controller前处理，process_response
         controller响应后处理。若process_request有响应返回，则返回，否则继续执行
        """
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.application)
        return self.process_response(response)


