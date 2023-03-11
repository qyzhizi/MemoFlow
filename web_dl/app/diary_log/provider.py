#!/usr/bin/env python
# coding=utf-8
import os
import logging
import json
import sqlite3

from web_dl.common import dependency
from web_dl.common import manager

LOG = logging.getLogger(__name__)


@dependency.provider('diary_log_api')
class Manager(object):
    driver_namespace = "diary_log_api"

    def get_html(self):
        
        with open("/root/git_rep/dl/web_dl/data/diary_log/index.html", "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_js(self):
        with open("/root/git_rep/dl/web_dl/data/diary_log/log.js", "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    def save_log(self, diary_log):
        conn = sqlite3.connect('diary_log.db')
        c = conn.cursor()
        LOG.info(diary_log['content'])
        c.execute('INSERT INTO diary_log  (content) VALUES (?)', (diary_log['content'],))
        conn.commit()
        # 关闭数据库连接
        conn.close()
    
    def get_logs(self):
        conn = sqlite3.connect('diary_log.db')
        c = conn.cursor()
        c.execute('SELECT content FROM diary_log')
        contents = [row[0] for row in c.fetchall()]
        return json.dumps({'logs': contents})
    
    def delete_all_log(self):
        conn = sqlite3.connect('diary_log.db')
        c = conn.cursor()
        # 执行DELETE语句，删除表中的所有数据
        c.execute('DELETE FROM diary_log')
        # 提交更改并关闭连接
        conn.commit()
        conn.close()

