#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import json
import requests
import re

from web_dl.common import dependency
from web_dl.common import manager
from web_dl.conf import CONF
from web_dl.api import notion_api
from web_dl.tasks import celery_task
from web_dl.db import diary_log as diary_log_db

LOG = logging.getLogger(__name__)

# driver_name = CONF.diary_log['driver']
DATA_BASE_PATH = CONF.diary_log['data_base_path']
DIARY_LOG_TABLE = CONF.diary_log['diary_log_table']
INDEX_HTML_PATH = CONF.diary_log['index_html_path']
LOG_JS_PATH = CONF.diary_log['log_js_path']

@dependency.provider('diary_log_api')
class Manager(object):
    driver_namespace = "diary_log_api"

    # def __init__(self):
    #     super().__init__(driver_name)

    def get_html(self, index_html_path=INDEX_HTML_PATH):
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_js(self, log_js_path=LOG_JS_PATH):
        with open(log_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    def save_log(self, content, tags, table_name=DIARY_LOG_TABLE,
                 data_base_path=DATA_BASE_PATH):
        """save diary(content, tags) to table

        Args:
            content (string): 笔记内容
            tags (list): 笔记的标签，例如：[a,b,c]
            table_name (string, optional): 表名. Defaults to DIARY_LOG_TABLE.
        """
        # data_base_path = CONF.diary_log['data_base_path']
        # conn = sqlite3.connect(data_base_path)
        # c = conn.cursor()
        # tags_string = ','.join(tags)
        # c.execute('INSERT INTO diary_log  (content, tags) VALUES (?,?)', (content,tags_string))
        # conn.commit()
        # # 关闭数据库连接
        # conn.close()
        tags_string = ','.join(tags)
        diary_log_db.inser_diary_to_table(table_name=table_name,
                                          content=content,
                                          tags=tags_string,
                                          data_base_path=data_base_path)
    
    def get_logs(self, table=DIARY_LOG_TABLE, columns=['content'],
                 data_base_path=DATA_BASE_PATH):
        """get all diary logs

        Args:
            table (string, optional): _description_. Defaults to DIARY_LOG_TABLE.
            columns (list, optional): _description_. Defaults to ['contents'].
            data_base_path (string, optional): _description_. Defaults to DATA_BASE_PATH.

        Returns:
            string: json string
        """
        # conn = sqlite3.connect(data_base_path)
        # c = conn.cursor()
        # c.execute(f'SELECT content FROM {table}')
        # contents = [row[0] for row in c.fetchall()]
        # return json.dumps({'logs': contents})
        rows = diary_log_db.get_all_logs(table_name=table,
                                         columns=columns,
                                         data_base_path=data_base_path)
        contents = [row[0] for row in rows]
        return json.dumps({'logs': contents})
    
    def delete_all_log(self, data_base_path=DATA_BASE_PATH, table=DIARY_LOG_TABLE):
        """delete all diary logs of one table

        Args:
            data_base_path (string, optional): 数据库地址. Defaults to DATA_BASE_PATH.
            table (string, optional): 表名. Defaults to DIARY_LOG_TABLE.
        """
        # conn = sqlite3.connect(data_base_path)
        # c = conn.cursor()
        # # 执行DELETE语句，删除表中的所有数据
        # c.execute(f'DELETE FROM {table}')
        # # 提交更改并关闭连接
        # conn.commit()
        # conn.close()
        diary_log_db.delete_all_log(table_name=table, data_base_path=data_base_path)
    
    # review provider
    def get_review_html(self, review_index_html_path):
        with open(review_index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    def get_review_js(self, review_js_path):
        with open(review_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res        
    
    def get_review_logs(self, table, columns, data_base_path):
        """get all diary logs

        Args:
            table (string, optional): _description_. Defaults to DIARY_LOG_TABLE.
            columns (list, optional): _description_. Defaults to ['contents'].
            data_base_path (string, optional): _description_. Defaults to DATA_BASE_PATH.

        Returns:
            string: json string
        """
        rows = diary_log_db.get_all_logs(table_name=table,
                                         columns=columns,
                                         data_base_path=data_base_path)
        contents = [row[0] for row in rows]
        return json.dumps({'logs': contents})

    def delete_all_review_log(self, data_base_path, table):
        """delete all diary logs of one table

        Args:
            data_base_path (string, optional): 数据库地址. Defaults to DATA_BASE_PATH.
            table (string, optional): 表名. Defaults to DIARY_LOG_TABLE.
        """
        diary_log_db.delete_all_log(table_name=table, data_base_path=data_base_path)

    # clipboard
    def get_clipboard_html(self, clipboard_html_path):
        with open(clipboard_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

    def get_clipboard_js(self, clipboard_js_path):
        with open(clipboard_js_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res
    
    def get_clipboard_logs(self, table_name, columns, data_base_path):
        """get all logs form one table columns

        Args:
            table_name (string): _description_
            columns (tuple or list): ["content"]
            data_base_path (tring): _description_

        Returns:
            list: [[content1], [content2], ...]
        """
        rows = diary_log_db.get_all_logs(table_name, columns, data_base_path)
        contents = [row[0] for row in rows]
        return json.dumps({'logs': contents})

    def save_log_to_clipboard_table(self,table_name, columns, data, data_base_path):
        diary_log_db.insert_columns_to_table(table_name=table_name,
                                                  columns=columns,
                                                  data=data,
                                                  data_base_path=data_base_path)
        



    def process_content(self, content):
        """
        用于生成卡片笔记

        content_list 的一个例子
        ['## 2023/3/24 03:15:14:', '#git #github #commit',
        '#que 如何展示在本地而不在远程的提交？', '#ans',
        'git log --oneline origin/main..HEAD']

        生成的效果：
        ## 2023/3/24 03:15:14:
        - #git #github #commit
        #que 如何展示在本地而不在远程的提交？  
        - #ans 
        git log --oneline origin/main..HEAD

        """
        content_list = content.split('\n')
        for i, content in enumerate(content_list):
            if content and (content.strip()[:4] == "#que"):
                up_line = i-1
                # 排除第0行，将上一行（带标签）当做子块
                up_line_list = content_list[up_line].strip()
                if up_line != 0 and up_line_list and up_line_list[0] == "#":
                    content_list[up_line] = " - " + content_list[up_line]
                else:
                    content_list[i] = " - " + content_list[i]

            # 这一行将视为特殊标签，并作为子块
            if content and (content.strip()[:4] == "#ans"):
                new_content = " - " + content
                content_list[i] = new_content
                LOG.info("new_content: %s" % new_content)
            
        # 重新组成串
        processed_content = "\n".join(content_list)
        # LOG.info("processed_content: %s" % processed_content)

        return processed_content
    
    def get_tags_from_content(self, content):
        """get tags

        Args:
            content (string): diary content

        Returns:
            list: tag list
        """
        # 匹配标签，找到所有的标签
        matches = re.findall(r"(?<!#)#\w+(?<!#)\s", content)
        tags = [match.strip('# \n') for match in matches]
        return tags
        
    def test_post_flomo(self):
        """
        flomo 笔记的api(不能泄露) ,可以向它发送内容
        POST https://flomoapp.com/iwh/MzA4ODk/bf5338***********3eb5b1b/
        Content-type: application/json
        {
            "content": "Hello, #flomo https://flomoapp.com"
        }
        """
        flomo_api_url = CONF.diary_log['flomo_api_url']
        post_data = { "content": "Hello, #flomo https://flomoapp.com" }
        requests.post(flomo_api_url, json=post_data)

    def send_log_flomo(self, flomo_post_data):
        flomo_api_url = CONF.diary_log['flomo_api_url']
        requests.post(flomo_api_url, json=flomo_post_data)

    # 向notion发送信息
    def send_log_notion(self, diary_log):
        return notion_api.create_database_page(CONF.diary_log['notion_api_key'],
                                                CONF.diary_log['database_id'],
                                                diary_log)
    
    # 向celery 发送异步任务
    def celery_send_log_notion(self, diary_log):
        return celery_task.celery_send_log_notion.delay(diary_log)
    
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
    
    # 向celery 发送异步任务
    def celery_update_file_to_github(self, token, repo, file_path, added_content, commit_message, branch_name):
        return celery_task.celery_update_file_to_github.delay(token, repo, file_path,
                                                              added_content,
                                                              commit_message,
                                                              branch_name)
        
    # 向坚果云发送异步任务，更新文件
    def celery_update_file_to_jianguoyun(self, base_url: str, acount: str,
                                         token: str, to_path: str, content: str,
                                         overwrite: bool = True) -> None:
        celery_task.update_file_to_janguoyun.delay(base_url, acount, token,
                                                   to_path, content, overwrite)

