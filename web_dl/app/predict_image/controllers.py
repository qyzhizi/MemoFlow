#!/usr/bin/env python
# coding=utf-8
import io
import logging
import json
from webob.response import Response
from PIL import Image

from web_dl.common import wsgi
from web_dl.common import dependency

LOG = logging.getLogger(__name__)

@dependency.requires('predict_image_api')
class Controllers(wsgi.Application):
    def predict_image(self, req):
        if req.method == 'POST':
            image_file = req.params.get('image')
        # Read the image in PIL format
        image = Image.open(io.BytesIO(image_file.file.read()))
        # Read pictures, preprocess and return picture data
        image = self.predict_image_api.prepare_image(req, image)
        # Image classification
        data = self.predict_image_api.predict_image(req, image)

        return json.dumps({"predict_result": data})

    def get_html(self, req):
        return self.predict_image_api.get_html()
    
