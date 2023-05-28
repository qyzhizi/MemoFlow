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

DATA_BASE_PATH = CONF.diary_log['data_base_path']
DIARY_LOG_TABLE = CONF.diary_log['diary_log_table']
REVIEW_DIARY_LOG = CONF.diary_log['review_diary_log_table']
INDEX_HTML_PATH = CONF.diary_log['index_html_path']
REVIEW_INDEX_HTML_PATH = CONF.diary_log['review_index_html_path']
LOG_JS_PATH = CONF.diary_log['log_js_path']
REVIEW_JS_PATH = CONF.diary_log['review_js_path']

#clipboard
CLIPBOARD_HTML_PATH = CONF.diary_log['clipboard_html_path']
CLIPBOARD_JS_PATH = CONF.diary_log['clipboard_js_path']
CLIPBOARD_LOG_TABLE = CONF.diary_log['clipboard_log_table'] #clipboard数据表名
CLIPBOARD_DATA_BASE_PATH = CONF.diary_log['clipboard_data_base_path'] #clipboard数据库路径

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

        # get tags
        tags = self.diary_log_api.get_tags_from_content(diary_log['content'])
        # 处理卡片笔记
        processed_content = self.diary_log_api.process_content(diary_log['content'])
        processed_block_content = self.diary_log_api.process_block(processed_content)

        # 保存到本地数据库
        self.diary_log_api.save_log(processed_content, tags)

        # # 发送到浮墨笔记
        # flomo_post_data = {"content": processed_content}
        # self.diary_log_api.send_log_flomo(flomo_post_data)

        # # 向notion 发送数据
        # self.diary_log_api.celery_send_log_notion(diary_log=processed_content)
        # # asyncio.run(self.diary_log_api.run_tasks(diary_log))

        # 向github仓库（logseq 笔记软件）发送数据
        if CONF.diary_log['send_to_github'] == True:
            file_path = CONF.diary_log['github_file_path']
            commit_message = "commit by web_dl"
            branch_name = "main"
            token = CONF.diary_log['github_token']
            repo = CONF.diary_log['github_repo']
            added_content = processed_block_content
            self.diary_log_api.celery_update_file_to_github(token,
                                                            repo,
                                                            file_path,
                                                            added_content,
                                                            commit_message,
                                                            branch_name)

        # 向坚果云发送异步任务，更新文件
        # 坚果云账号
        if CONF.diary_log['send_to_jianguoyun'] == True:
            JIANGUOYUN_COUNT = CONF.api_conf.JIANGUOYUN_COUNT
            JIANGUOYUN_TOKEN = CONF.api_conf.JIANGUOYUN_TOKEN
            base_url = CONF.api_conf.base_url
            to_path = CONF.api_conf.JIANGUOYUN_TO_PATH
            added_content = processed_block_content
            self.diary_log_api.celery_update_file_to_jianguoyun(base_url,
                                                                JIANGUOYUN_COUNT,
                                                                JIANGUOYUN_TOKEN,
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

    # review
    def get_review_html(self, req):
        return self.diary_log_api.get_review_html(
            review_index_html_path=REVIEW_INDEX_HTML_PATH)

    def get_review_js(self, req):
        return self.diary_log_api.get_review_js(review_js_path=REVIEW_JS_PATH)

    def get_review_logs(self, req):
        return self.diary_log_api.get_review_logs(table=REVIEW_DIARY_LOG,
                                                  columns=['content'],
                                                  data_base_path=DATA_BASE_PATH)

    def delete_all_review_log(self, req):
        return self.diary_log_api.delete_all_review_log(data_base_path=DATA_BASE_PATH,
                                                        table=REVIEW_DIARY_LOG)

    # clipboard
    def get_clipboard_html(self, req):
        return self.diary_log_api.get_clipboard_html(
            clipboard_html_path=CLIPBOARD_HTML_PATH)
    
    def get_clipboard_js(self, req):
        return self.diary_log_api.get_clipboard_js(
            clipboard_js_path=CLIPBOARD_JS_PATH)

    def get_clipboard_logs(self, req):
        return self.diary_log_api.get_clipboard_logs(
            table_name=CLIPBOARD_LOG_TABLE,
            columns=['content'],
            data_base_path=CLIPBOARD_DATA_BASE_PATH)
    
    def clipboard_addlog(self, req):
        # 从请求中获取POST数据
        data = req.body
        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log json_data:, %s" % diary_log["content"][:70])
        # 保存到本地数据库
        self.diary_log_api.save_log_to_clipboard_table(
            table_name=CLIPBOARD_LOG_TABLE,
            columns=['content'],
            data = [diary_log["content"]],
            data_base_path=CLIPBOARD_DATA_BASE_PATH
            )
        return json.dumps(diary_log) # data 是否可行？

            