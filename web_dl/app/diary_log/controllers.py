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
        LOG.info("diary_log json_data:, %s" % diary_log["content"][:70])

        # 处理卡片笔记
        processed_content = self.diary_log_api.process_content(diary_log['content'])

        # 保存到本地数据库
        self.diary_log_api.save_log(processed_content)

        # 发送到浮墨笔记
        flomo_post_data = {"content": processed_content}
        self.diary_log_api.send_log_flomo(flomo_post_data)

        # 向notion 发送数据
        self.diary_log_api.celery_send_log_notion(diary_log=processed_content)
        # asyncio.run(self.diary_log_api.run_tasks(diary_log))

        # 向github仓库（logseq 笔记软件）发送数据
        file_path = "pages/github_cards.md"
        commit_message = "commit by web_dl"
        branch_name = "main"
        token = CONF.diary_log['github_token']
        repo = CONF.diary_log['github_repo']
        added_content = processed_content
        self.diary_log_api.celery_update_file_to_github(token,
                                                        repo,
                                                        file_path,
                                                        added_content,
                                                        commit_message,
                                                        branch_name)

        # 向坚果云发送异步任务，更新文件
        # lzp 的坚果云账号
        lzp_jianguoyun_count = CONF.api_conf.lzp_jianguoyun_count
        lzp_jianguoyun_token = CONF.api_conf.lzp_jianguoyun_token
        base_url = CONF.api_conf.base_url
        to_path = CONF.api_conf.lzp_jianguoyun_to_path
        added_content = processed_content
        self.diary_log_api.celery_update_file_to_jianguoyun(base_url,
                                                            lzp_jianguoyun_count,
                                                            lzp_jianguoyun_token,
                                                            to_path,
                                                            added_content,
                                                            overwrite = True)

        return json.dumps({"content": processed_content})
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
