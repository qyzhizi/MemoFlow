#!/usr/bin/env python
# coding=utf-8
import logging
import json
import requests
import sqlite3

from web_dl.common import dependency
from web_dl.common import manager
from web_dl.conf import CONF

LOG = logging.getLogger(__name__)


@dependency.provider('diary_log_lrx_api')
class Manager(object):
    driver_namespace = "diary_log_lrx_api"

    def get_html(self):
        index_html_path = CONF.diary_log_lrx['index_html_path']
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_js(self):
        log_js_path = CONF.diary_log_lrx['log_js_path']
        with open(log_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    def save_log(self, diary_log_lrx):
        data_base_path = CONF.diary_log_lrx['data_base_path']
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        LOG.info(diary_log_lrx['content'])
        c.execute('INSERT INTO diary_log_lrx  (content) VALUES (?)', (diary_log_lrx['content'],))
        conn.commit()
        # 关闭数据库连接
        conn.close()
    
    def get_logs(self):
        data_base_path = CONF.diary_log_lrx['data_base_path']
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        c.execute('SELECT content FROM diary_log_lrx')
        contents = [row[0] for row in c.fetchall()]
        return json.dumps({'logs': contents})
    
    def delete_all_log(self):
        data_base_path = CONF.diary_log_lrx['data_base_path']
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        # 执行DELETE语句，删除表中的所有数据
        c.execute('DELETE FROM diary_log_lrx')
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
    
    """
    flomo 笔记的api(不能泄露) ,可以向它发送内容
    POST https://flomoapp.com/iwh/MzA4ODk/bf5338002eb49cbd323c672e03eb5b1b/
    Content-type: application/json
    {
        "content": "Hello, #flomo https://flomoapp.com"
    }
    """
    def test_post_flomo(self):
        flomo_api_url = CONF.diary_log_lrx['flomo_api_url']
        post_data = { "content": "Hello, #flomo https://flomoapp.com" }
        requests.post(flomo_api_url, json=post_data)

    def send_log_flomo(self, diary_log_lrx):
        flomo_api_url = CONF.diary_log_lrx['flomo_api_url']
        post_data = diary_log_lrx
        requests.post(flomo_api_url, json=post_data)
