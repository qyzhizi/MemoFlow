# coding=utf-8
from memoflow.core import wsgi
from memoflow.app.predict_image import controllers

class Router(wsgi.ComposableRouter):
    def add_routes(self, mapper):
        predict_controller = controllers.Controllers()
        # "/v1/predict-image/index.html" is wrong, 
        # "/v1" must be removed
        mapper.connect('/predict-image/index.html',
                controller=predict_controller,
                action='get_html',
                conditions=dict(method=['GET']))
        mapper.connect('/predict-image',
                       controller=predict_controller,
                       action='predict_image',
                       conditions=dict(method=['POST'])
                      )
