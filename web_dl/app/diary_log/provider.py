#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import json
import requests
import sqlite3

from web_dl.common import dependency
from web_dl.common import manager
from web_dl.conf import CONF
from web_dl.app.diary_log.driver import notion_api

LOG = logging.getLogger(__name__)


@dependency.provider('diary_log_api')
class Manager(object):
    driver_namespace = "diary_log_api"

    def get_html(self):
        index_html_path = CONF.diary_log['index_html_path']
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_js(self):
        log_js_path = CONF.diary_log['log_js_path']
        with open(log_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    def save_log(self, diary_log):
        data_base_path = CONF.diary_log['data_base_path']
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        LOG.info(diary_log['content'])
        c.execute('INSERT INTO diary_log  (content) VALUES (?)', (diary_log['content'],))
        conn.commit()
        # 关闭数据库连接
        conn.close()
    
    def get_logs(self):
        data_base_path = CONF.diary_log['data_base_path']
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        c.execute('SELECT content FROM diary_log')
        contents = [row[0] for row in c.fetchall()]
        return json.dumps({'logs': contents})
    
    def delete_all_log(self):
        data_base_path = CONF.diary_log['data_base_path']
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        # 执行DELETE语句，删除表中的所有数据
        c.execute('DELETE FROM diary_log')
        # 提交更改并关闭连接
        conn.commit()
        conn.close()

    """
    flomo 笔记的api(不能泄露) ,可以向它发送内容
    POST https://flomoapp.com/iwh/MzA4ODk/bf5338***********3eb5b1b/
    Content-type: application/json
    {
        "content": "Hello, #flomo https://flomoapp.com"
    }
    """
    def test_post_flomo(self):
        flomo_api_url = CONF.diary_log['flomo_api_url']
        post_data = { "content": "Hello, #flomo https://flomoapp.com" }
        requests.post(flomo_api_url, json=post_data)

    def send_log_flomo(self, diary_log):
        flomo_api_url = CONF.diary_log['flomo_api_url']
        post_data = diary_log
        requests.post(flomo_api_url, json=post_data)

    # 向notion发送信息
    def send_log_notion(self, diary_log):
        return notion_api.create_database_page(CONF.diary_log['notion_api_key'],
                                                CONF.diary_log['database_id'],
                                                diary_log['content'])
    
    # 定义一个异步任务
    async def async_send_log_flomo(self, diary_log):
        LOG.info("*****start task async_send_log_flomo")
        # await asyncio.sleep(5)
        self.send_log_flomo(diary_log)
        LOG.info("*****end task async_send_log_flomo")
    
    # # 定义一个异步任务
    async def async_send_log_notion(self, diary_log):
        LOG.info("******start task async_send_log_notion")
        # await asyncio.sleep(5)
        self.send_log_notion(diary_log)
        LOG.info("******end task async_send_log_notion")

    # 定义一个协程， 用于并发执行多个任务 ,异步额外消耗时间太长了（3秒到8秒），放弃
    async def run_tasks(self, diary_log):
        # 创建一个任务列表
        tasks = []
        task = asyncio.create_task(self.async_send_log_flomo(diary_log))
        tasks.append(task)

        task = asyncio.create_task(self.async_send_log_notion(diary_log))
        tasks.append(task)

        # 并发执行任务
        await asyncio.gather(*tasks)
        