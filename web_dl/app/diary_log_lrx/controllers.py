#!/usr/bin/env python
# coding=utf-8
import logging
import json

from web_dl.conf import CONF
from web_dl.common import wsgi
from web_dl.common import dependency

LOG = logging.getLogger(__name__)

@dependency.requires('diary_log_api')
@dependency.requires('diary_log_lrx_api')
class DiaryLog(wsgi.Application):
    def get_html(self, req):
        return self.diary_log_lrx_api.get_html()

    def get_js(self, req):
        return self.diary_log_lrx_api.get_js()

    def add_log(self, req):
        # 从请求中获取POST数据
        data = req.body
        
        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log_lrx json_data:, %s" % diary_log)

        # 保存到本地数据库
        self.diary_log_lrx_api.save_log(diary_log)
        # 发送到浮墨笔记
        # self.diary_log_lrx_api.send_log_flomo(diary_log)

        # 保存到github
        added_content = diary_log['content']
        file_path = "pages/github_cards.md"
        commit_message = "commit by web_dl"
        branch_name = "main"
        token = CONF.diary_log['github_token']
        repo = CONF.diary_log['github_repo']

        self.diary_log_api.celery_update_file_to_github(token,
                                                        repo,
                                                        file_path,
                                                        added_content,
                                                        commit_message,
                                                        branch_name)

        # 将json转换json字符串返回
        return json.dumps(diary_log)
        # return Response(json_data)
    
    def get_logs(self, req):
        return self.diary_log_lrx_api.get_logs()

    def delete_all_log(self, req):
        return self.diary_log_lrx_api.delete_all_log()
    
    def test_flomo(self, req):
        self.diary_log_lrx_api.test_post_flomo()
        return "sucess"
