# coding=utf-8
from web_dl.common import wsgi
from web_dl.app.predict_image import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        predict_controller = controllers.Controllers()
        mapper.connect('/predict-image',
                       controller=predict_controller,
                       action='predict_image',
                       conditions=dict(method=['POST'])
                      )
