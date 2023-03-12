#!/usr/bin/env python
# coding=utf-8
import os
import logging
import json
import sqlite3

from web_dl.common import dependency
from web_dl.common import manager
from web_dl.conf import CONF

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

