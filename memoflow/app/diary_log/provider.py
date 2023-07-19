#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import json
import requests
import re

from memoflow.core import dependency
from memoflow.core import manager
from memoflow.conf import CONF
from memoflow.api import notion_api
from memoflow.tasks import celery_task
from memoflow.db import diary_log as diary_log_db

LOG = logging.getLogger(__name__)

# driver_name = CONF.diary_log['driver']
DATA_BASE_PATH = CONF.diary_log['data_base_path']
DIARY_LOG_TABLE = CONF.diary_log['diary_log_table']

@dependency.provider('diary_log_api')
class Manager(manager.Manager):
    driver_namespace = "memoflow.app.diary_log.driver"

    def __init__(self):
        super(Manager, self).__init__(CONF.diary_log.driver)

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
        
    def process_block(self, block_string):
        """处理子块缩进
        block_string: 使用process_content函数处理后的字符串,它在特的行
        添加了子块标识"\t- "，一般地：`"\t"*n+"- "` 其中"\t"的数目n大于等于0

        Returns:
            _type_: 处理后的字符串
        例如：
        处理前的字符串：
        ```
        - ## 2023年5月13日 下午1:53:49:
        这是最上层的子块，也是第一个子块
            - #webdl #tab #制表符
        这是第二层子块
        #que 在笔记页面中输入制表符
            - #ans
        这也是第二层子块
        快捷键: alt + q
        因为前段的js设置了该快捷键
        ```
        处理后的字符串：
        ```
        - ## 2023年5月13日 下午1:53:49:
            这是最上层的子块，也是第一个子块
            - #webdl #tab #制表符
                这是第二层子块
                #que 在笔记页面中输入制表符
            - #ans
                这也是第二层子块
                快捷键: alt + q
                因为前段的js设置了该快捷键
        ```
        """
        
        """
        另外一个更复杂的例子：

        s = '''- ## 2023-5-10
        top block
        \t- item1
        509348606-
        \t\t-    item1.1
        45834056843

        \t\t\t- item1.2
        \t\t\t    405843068045
        \t- item2
        3405834056
        '''
        items = re.split(r'(\t+-\s+)', block_string)
        items:  ['## 2023-5-10\nssssssssssssssssssssss',
        '\t- ', 'item1\n509348606-\n',
        '\t\t-    ', 'item1.1\n\t\t\t    45834056843\n',
        '\t\t\t- ', 'item1.2\n\t\t\t    405843068045\n',
        '\t- ', 'item2\n3405834056\n']
        result:
        ```
        - ## 2023-5-10
          top block
        - item1
                - item1.1
                  45834056843

                        - item1.2
                          405843068045
        - item2
          3405834056
        ```
        """
        processed_result = []

        items = re.split(r'(\t+-\s+)', block_string)

        # 假设block_string以`- ## 2023-5-10`开头，
        # 开头是第一个block,但该block不带"\t", 额外做处理，变为0个"\t"
        # 之所以这样处理，是因为`- `很常见，不能直接使用上面那样的正则匹配
        if items[0].startswith("- "):
            # items[0] 分割成两部分：'- ' , items[0][2:]
            items = ['- ' , items[0][2:]] + items[1:]
        else:
            # 额外添加'- '，把第一行默认做一个子块，
            # 比如：block_string 以`## 2023-5-10`开头
            items = ['- ' , items[0]] + items[1:]

        child_block_list = []
        #子块(block)与"\t"的个数是成对的, 偶数个
        for i in range(0, len(items), 2):
            if i+1 < len(items):
                t_list = items[i].split("-")
                t_num = len(t_list[0])
                child_block_list.append((t_num, items[i+1]))

        # 处理每个子块
        for i, (t_num, item) in enumerate(child_block_list):
            #得到每一行，相当于logseq的软回车的行
            lines = item.split('\n')
            # split('\n')操作会可能会多得到一个空字符串, 去除最后一个空字符串
            if lines[-1].strip(" ") == "":
                lines = lines[:-1]
            for line_index, line in enumerate(lines):
                # 子块第一行，比较特殊，最多给一个"\t"，或者不给"\t"
                # 因为已经把最上层的子块考虑进来了，例如：`- ## 2023-5-10`
                # i == 0时， t_num一般是等于0的
                if i == 0 and t_num > 1:
                    t_num = 1
                # 当前子块如果比上个子块多2个、2个以上的"\t"，进行现在，最多只能多一个"\t"
                if i-1 >= 0 and t_num >= child_block_list[i-1][0] +1:
                    t_num = child_block_list[i-1][0] +1
                # 判断是否为block开头标识：t_num*'\t'+ "- "
                if line_index == 0:
                    pre_str = t_num*'\t'+ "- "
                else:
                    # 软回车标识
                    pre_str = t_num*'\t'+ "  "
                    # 匹配开头“\t\t  ”, 多个"\t", 至少两个空格
                    match = re.match(r'^\x20{0,}\t+\x20{2,}', line)
                    if match is not None:
                        #统一先删除，后面再加上
                        # print([match[0]])
                        line = line[len(match[0]):]

                #加上t_num*'\t'+ "  " 或者t_num*'\t'+ "- "
                processed_result.append(pre_str + line)
        return "\n".join(processed_result)

    def process_content(self, content):
        """
        用于生成卡片笔记

        content_list 的一个例子
        ['## 2023/3/24 03:15:14:', '#git #github #commit',
        '#que 如何展示在本地而不在远程的提交？', '#ans',
        'git log --oneline origin/main..HEAD']

        生成的效果：
        ```
        - ## 2023/3/24 03:15:14:
        \t- #git #github #commit
        #que 如何展示在本地而不在远程的提交？  
        \t- #ans 
        git log --oneline origin/main..HEAD
        ```
        新增例子:
        输入:
        ```
        ## 2023/5/14 07:11:00:
        --todo sdfjslfjds
        @blk djfslfjs
        @blk
        djfsfjsfjds;
        ```
        生成效果：
        ```
        - ## 2023/5/14 07:11:00:
        \t- TODO sdfjslfjds
        \t- @blk djfslfjs
        \t- @blk
        djfsfjsfjds;
        ```        
        """
        title_string = "##"
        tag_string = "#"
        block_pre_string = ["- ", "\t- "]
        que_strings = ["#que ", "#que"]
        ans_strings = ["#ans ", "#ans"]
        normal_blk_strings = ["@blk ", "@blk"]

        todo_key = ["--todo ", "--TODO ",
                    "--done ", "--DONE "]
        todo_value = ["\t- TODO ", "\t- DONE "]
        todo_map = {todo_key[0]:todo_value[0],
                    todo_key[1]:todo_value[0],
                    todo_key[2]:todo_value[1],
                    todo_key[3]:todo_value[1]}

        content_list = content.split('\n')
        for i, content in enumerate(content_list):
            if i == 0 and content.strip()[:len(title_string)] == title_string:
                # 第一个时间戳标题需要设置为logseq最上层的子块，所以不带"\t"
                content_list[i] = block_pre_string[0] + content_list[i]
            
            # que_strings = ["#que ", "#que"]
            if content and (content.strip()[:len(que_strings[0])] == que_strings[0]
                            or content.strip()==que_strings[1]):
                up_line = i-1
                # 排除第0行，将上一行（带标签）当做子块
                up_line_list = content_list[up_line].strip()
                if up_line != 0 and content_list[up_line].startswith(block_pre_string[1]):
                    continue
                if up_line != 0 and up_line_list and up_line_list[0] == tag_string:
                    content_list[up_line] = block_pre_string[1] + content_list[up_line]
                else:
                    content_list[i] = block_pre_string[1] + content_list[i]

            # 这一行将视为特殊标签，并作为子块
            # ans_strings = ["#ans ", "#ans"]
            if content and (content.strip()[:len(ans_strings[0])] == ans_strings[0]
                            or content.strip()==ans_strings[1]):
                new_content = block_pre_string[1] + content
                content_list[i] = new_content

            # 解析`-todo ` 变为子块
            if content and (content.strip()[:len(todo_key[0])] in todo_map
                            or content.strip() in todo_map):
                new_content = todo_map[content.strip()[:len(todo_key[0])]] + content[
                    len(todo_key[0]):]
                content_list[i] = new_content

            # 解析`@blk` 变为子块
            # normal_blk_strings = ["@blk ", "@blk"]
            if content and (content.strip()[:len(normal_blk_strings[0])]==normal_blk_strings[0]
                            or content.strip()==normal_blk_strings[1]):
                new_content = block_pre_string[1] + content
                content_list[i] = new_content

        # 重新组成串,并去除前后的空格与换行符等空白字符
        return "\n".join(content_list).strip()
    
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
    def celery_update_file_to_github(self, token, repo, file_path,
                                     added_content, commit_message,
                                     branch_name):
        return celery_task.celery_update_file_to_github.delay(token, repo,
                                                              file_path,
                                                              added_content,
                                                              commit_message,
                                                              branch_name)
        
    # 向坚果云发送异步任务，更新文件
    def celery_update_file_to_jianguoyun(self, base_url: str, acount: str,
                                         token: str, to_path: str, content: str,
                                         overwrite: bool = True) -> None:
        celery_task.update_file_to_janguoyun.delay(base_url, acount, token,
                                                   to_path, content, overwrite)

    # 同步任务，批量获取 github 文件内容
    def get_contents_from_github(self, token, repo, sync_file_path_list,
                                 branch_name):
        contents = self.driver.get_contents_from_github(token, repo,
                                                    sync_file_path_list,
                                                    branch_name)
        return contents
    
    # sync contents to database
    def sync_contents_to_db(self, contents, table_name, data_base_path):
        self.driver.sync_contents_to_db(contents, table_name, data_base_path)