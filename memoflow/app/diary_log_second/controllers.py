#!/usr/bin/env python
# coding=utf-8
import logging
import json

from memoflow.conf import CONF
from memoflow.core import wsgi
from memoflow.core import dependency

LOG = logging.getLogger(__name__)

@dependency.requires('diary_log_api')
@dependency.requires('diary_log_second_api')
class DiaryLog(wsgi.Application):
    def get_html(self, req):
        return self.diary_log_second_api.get_html()

    def get_js(self, req):
        return self.diary_log_second_api.get_js()

    def add_log(self, req):
        # 从请求中获取POST数据
        data = req.body
        
        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log_second json_data:, %s" % diary_log)

        # 处理卡片笔记
        processed_content = self.diary_log_api.process_content(diary_log['content'])

        # 保存到本地数据库
        self.diary_log_second_api.save_log(processed_content)
        # 发送到浮墨笔记
        # self.diary_log_second_api.send_log_flomo(diary_log)

        # 保存到github
        # added_content = diary_log['content']
        # file_path = "pages/github_cards.md"
        # commit_message = "commit by memoflow"
        # branch_name = "main"
        # token = CONF.diary_log['GITHUB_TOKEN']
        # repo = CONF.diary_log['GITHUB_REPO']

        # self.diary_log_api.celery_update_file_to_github(token,
        #                                                 repo,
        #                                                 file_path,
        #                                                 added_content,
        #                                                 commit_message,
        #                                                 branch_name)
        
        # 向坚果云发送异步任务，更新文件
        # second 的坚果云账号
        second_jianguoyun_count = CONF.api_conf.second_jianguoyun_count
        second_jianguoyun_token = CONF.api_conf.second_jianguoyun_token
        base_url = CONF.api_conf.base_url
        to_path = CONF.api_conf.second_jianguoyun_to_path
        added_content = processed_content
        self.diary_log_api.celery_update_file_to_jianguoyun(base_url,
                                                            second_jianguoyun_count,
                                                            second_jianguoyun_token,
                                                            to_path,
                                                            added_content,
                                                            overwrite = True)

        # 将json转换json字符串返回
        return json.dumps({"content": processed_content})
        # return Response(json_data)
    
    def get_logs(self, req):
        return self.diary_log_second_api.get_logs()

    def delete_all_log(self, req):
        return self.diary_log_second_api.delete_all_log()
    
    def test_flomo(self, req):
        self.diary_log_second_api.test_post_flomo()
        return "sucess"
