#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import json
import time

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

        # 保存到本地数据库
        self.diary_log_api.save_log(diary_log)
        # start_time = time.time()
        # # 发送到浮墨笔记
        # self.diary_log_api.send_log_flomo(diary_log)

        # # 发送到notion 数据库
        # self.diary_log_api.send_log_notion(diary_log)
        # end_time = time.time()
        # LOG.info(f'Function took {(end_time - start_time):.5f} seconds to run.')

        start_time = time.time()
        self.diary_log_api.celery_send_log_notion(diary_log)
        # asyncio.run(self.diary_log_api.run_tasks(diary_log))
        end_time = time.time()
        LOG.info(f'Function took {(end_time - start_time):.5f} seconds to run.')

        return json.dumps(diary_log)
        # return Response(json_data)
    
    def get_logs(self, req):
        return self.diary_log_api.get_logs()

    def delete_all_log(self, req):
        return self.diary_log_api.delete_all_log()

    def delete_all_log(self, req):
        return self.diary_log_api.delete_all_log()
    
    def test_flomo(self, req):
        self.diary_log_api.test_post_flomo()
        return "sucess"
