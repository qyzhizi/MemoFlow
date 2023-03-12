#!/usr/bin/env python
# coding=utf-8
import os
import openai
import logging
import json
import sqlite3

from webob.response import Response

from web_dl.common import wsgi
from web_dl.common import dependency

LOG = logging.getLogger(__name__)


@dependency.requires('diary_log_api')
class DiaryLog(wsgi.Application):
    def get_html(self, req):
        return self.diary_log_api.get_html()

    def get_js(self, req):
        return self.diary_log_api.get_js()

    def add_log(self, req):
        # 从请求中获取POST数据
        data = req.body
        
        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log json_data:, %s" % diary_log)

        self.diary_log_api.save_log(diary_log)

        return json.dumps(diary_log)
        # return Response(json_data)
    
    def get_logs(self, req):
        return self.diary_log_api.get_logs()

    def delete_all_log(self, req):
        return self.diary_log_api.delete_all_log()