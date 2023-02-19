#!/usr/bin/env python
# coding=utf-8
from webob.response import Response
from web_dl.common import wsgi
from web_dl.common import dependency


@dependency.requires('predict_image_api')
class Controllers(wsgi.Application):
    def predict_image(self, req, image):

        # Read the image in PIL format
        log.info("read image, type of readed image: %s", type(image))
        image = image.read()
        image = Image.open(io.BytesIO(image))
        log.info("type of Image.opened image: %s", type(image))

        # 读取图片,预处理 返回图片数据
        image = self.predict_image_api.prepare_image(req, image)
        # 图片分类
        data = self.predict_image_api.predict_image(req, image)

        
    
