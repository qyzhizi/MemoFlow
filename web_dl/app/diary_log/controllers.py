#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import json
import time

from web_dl.conf import CONF
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

        # 发送到浮墨笔记
        self.diary_log_api.send_log_flomo(diary_log)

        # # 发送到notion 数据库
        # self.diary_log_api.send_log_notion(diary_log)

        """
        added_list 的一个例子
        ['## 2023/3/24 03:15:14:', '#test #webdl', '#que 是否可行？', '#ans 还行', '']
        """
        added_content = diary_log['content']
        added_list = added_content.split('\n')
        if len(added_list) > 1:
            # 作为子块
            added_list[1] = " - " + added_list[1]
        if len(added_list) > 3:
            # 作为子块
            added_list[3] = " - " + added_list[3]
        # 重新组成串
        added_content = "\n".join(added_list)

        # 向notion 发送数据
        self.diary_log_api.celery_send_log_notion(diary_log=added_content)
        # asyncio.run(self.diary_log_api.run_tasks(diary_log))

        # 向github仓库（logseq 笔记软件）发送数据
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
