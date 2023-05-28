#!/usr/bin/env python
# coding=utf-8
import os
import openai
import logging
import json

from webob.response import Response

from web_dl.core import wsgi
from web_dl.core import dependency

LOG = logging.getLogger(__name__)

@dependency.requires('test_api')
class Test(wsgi.Application):
    def test(self, req, name):
        test = self.test_api.test
        return Response("hello world %s, %s" % (name, test))

    def test_chatgpt(self, req, question):
        openai.api_key = "******************"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question+"\n",
            temperature=0.7,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )

        LOG.info(response["choices"][0]["text"])

        return response["choices"][0]["text"]

    def get_html(self, req):
        return self.test_api.get_html()
    
    def add_diary(self, req):
        # Get post data from request
        data = req.body
        
        # Convert post data to json format
        json_data = json.loads(data)
        LOG.info("data:, %s" % json_data)
        return Response(json.dumps(json_data))

