#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import json
from datetime import datetime
from datetime import timedelta
import requests
import uuid
from webob import Request
import urllib.request
import re

from memoflow.core import dependency
from memoflow.core import manager
from memoflow.conf import CONF
from memoflow.api import notion_api
from memoflow.utils.token_jwt import TokenManager
from memoflow.api.github_api import GitHupApi
from memoflow.utils.common import username_to_table_name
from memoflow.exception.visiable_exc import VisibleException

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
)

LOG = logging.getLogger(__name__)

# driver_name = CONF.diary_log['driver']
USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']
SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']

@dependency.provider('diary_log_api')
class Manager(manager.Manager):
    driver_namespace = "memoflow.app.diary_log.driver"

    def __init__(self):
        super(Manager, self).__init__(CONF.diary_log.driver)
        # #debug
        # from memoflow.app.diary_log.driver.backend import DiaryLogDriver
        # self.driver = DiaryLogDriver()

    def generate_token(self, user_id, expires):
        return TokenManager.generate_token(user_id, expires)

    def verify_token(self, token):
        return TokenManager.verify_token(token)

    def get_access_token(self, code):

        CLIENT_SECRET = CONF.diary_log['CLIENT_SECRET']
        CLIENT_ID = CONF.diary_log['CLIENT_ID']
        # 回调 URL，需与 GitHub App 中设置的一致
        # REDIRECT_URI = '/v1/diary-log/github-authenticate-callback'

        # 使用 code 获取访问令牌
        token_url = 'https://github.com/login/oauth/access_token'
        payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            # 'redirect_uri': REDIRECT_URI
        }
        headers = {'Accept': 'application/json'}

        # 创建 POST 请求对象
        request = Request.blank(token_url, method='POST',
                                POST=payload, headers=headers)
        try:
            # 发送请求
            response = request.get_response()
        except Exception as e:
            LOG.error(e)
            raise e

        # 解析响应内容
        if response.status_code == 200:
            # print(response.json())
            data = json.loads(response.text)
            # access_token = data.get('access_token', None)
            # if not access_token:
            #     # return 'Failed to retrieve access token'
            #     LOG.error('Failed to retrieve access token')
            return data
        else:
            return None

    def get_github_access_token_by_refresh_token(self, refresh_token):
        # 参考：
        # https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/refreshing-user-access-tokens

        CLIENT_SECRET = CONF.diary_log['CLIENT_SECRET']
        CLIENT_ID = CONF.diary_log['CLIENT_ID']
        token_url = 'https://github.com/login/oauth/access_token'
        payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': "refresh_token",
            'refresh_token': refresh_token
        }
        headers = {'Accept': 'application/json'}

        # 创建 POST 请求对象
        # request = Request.blank(token_url, method='POST',
        #                         POST=payload, headers=headers)
        # # 发送请求
        # response = request.get_response()

        # 将 payload 转换为字节类型的数据
        data = urllib.parse.urlencode(payload).encode('utf-8')
        request = urllib.request.Request(
            token_url, method='POST', data=data, headers=headers)

        # 发送请求
        # 使用 urlopen 发送请求，并设置超时时间为2秒
        try:
            response = urllib.request.urlopen(request, timeout=2)
        except Exception as e:
            LOG.exception(str(e))
        if response.getcode() == 200:
            data = json.loads(response.read())
            if "access_token" not in data:
                LOG.error(f"access_token not in response, response: {data}")
                raise Exception("Network Error, Can't get accesstoken by refresh token")
                # return None
            return data
        elif response.getcode() != 200 :
            data = json.loads(response.read())
            LOG.error(f"Network Error, Can't get accesstoken by refresh token: {data}")
            raise Exception("Network Error, Can't get accesstoken by refresh token")

    def process_github_tokens_info_to_db_format(self, github_tokens_info):
        access_token = github_tokens_info.get('access_token', None)
        github_access_token_expires_in = github_tokens_info.get('expires_in', None)
        refresh_token = github_tokens_info.get('refresh_token', None)
        github_refresh_token_expires_in = github_tokens_info.get('refresh_token_expires_in', None)

        # 获取当前时间
        current_time = datetime.now()

        # 增加 github_access_token_expires_in 秒（8小时），然后减去120秒
        access_token_expires_at = current_time + timedelta\
            (seconds=(github_access_token_expires_in - 120))
        refresh_token_expires_at = current_time + timedelta\
            (seconds=(github_refresh_token_expires_in - 120))

        github_tokens_info = {
            'access_token': access_token,
            'access_token_expires_at': access_token_expires_at,
            'refresh_token': refresh_token,
            'refresh_token_expires_at': refresh_token_expires_at,
        }
        return github_tokens_info

    def test_github_access(
            self,
            access_token,
            github_repo_name
            ):
        return self.driver.test_github_access(
            access_token=access_token, github_repo_name=github_repo_name)
    
    def test_jianguoyun_access(
            self,
            jianguoyun_account:str,
            jianguoyun_token: str,
    ):
        return self.driver.test_jianguoyun_access(
            jianguoyun_account=jianguoyun_account,
            jianguoyun_token=jianguoyun_token)

    def init_sync_files_for_github(
        self,
        access_token:str,
        github_repo_name:str,
        current_sync_file:str,
        other_sync_file_list:str
    ):
        """ create sync file if file not exist in github repo.
        current_sync_file: the file path in github repo,
        other_sync_file_list: the file path in github repo,
        split by ',', and space is optional.
        example:
        current_sync_file = '/diary_log/diary_log.md'

        Args:
            access_token (str): _description_
            github_repo_name (str): _description_
            current_sync_file (str): _description_
            other_sync_file_list (str): _description_
        """
        other_sync_file_list = [path.strip() for path in
                                 other_sync_file_list.split(',')] \
            if other_sync_file_list else []
        all_sync_files = other_sync_file_list + ([current_sync_file]
                                                 if current_sync_file else [])
        self.driver.create_file_if_not_exist_in_github(
            access_token=access_token,
            github_repo_name=github_repo_name,
            files_paths=all_sync_files)

    def init_sync_files_for_jianguoyun(
            self,
            jianguoyun_account:str,
            jianguoyun_token: str,
            current_sync_file: str,
            other_sync_file_list: str):
        """ create sync file if file not exist in jianguoyun.
        current_sync_file: the file path in jianguoyun,
        other_sync_file_list: the file path in jianguoyun,
        split by ', ', and space is optional.
        example:
        current_sync_file = '/diary_log/diary_log.md'

        Args:
            jianguoyun_account (str): _description_
            jianguoyun_token (str): _description_
            current_sync_file (str): _description_
            other_sync_file_list (str): _description_
        """
        other_sync_file_list = [path.strip() for path in
                                 other_sync_file_list.split(',')] \
            if other_sync_file_list else []
        all_sync_files = other_sync_file_list + ([current_sync_file]
                                                 if current_sync_file else [])
        self.driver.create_file_if_not_exist_in_jianguoyun(
            jianguoyun_account=jianguoyun_account,
            jianguoyun_token=jianguoyun_token,
            all_sync_files=all_sync_files)

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

        pattern = r'(\t+-[\x20]|\t-@ans[\x20])'
        items = re.split(pattern, block_string)

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
                if len(t_list) > 1 and t_list[1] == "@ans ":
                    # norm ans child block
                    t_num = (1, "@ans ")
                else:
                    t_num = len(t_list[0])
                child_block_list.append((t_num, items[i+1]))

        # 处理每个子块
        for i, (t_num, item) in enumerate(child_block_list):
            if t_num == (1, "@ans "):
                t_num = 1
                child_block_list[i] = (t_num, item)
                ans_normal_block = True
            else:
                ans_normal_block = False
            # 去除子块最后一行末尾的空白字符(包括\t \n), logseq 格式
            item = item.rstrip()
            #得到每一行，相当于logseq的软回车的行
            lines = item.split('\n')
            # split('\n')操作会可能会多得到一个空字符串, 去除最后一个空字符串
            if lines[-1].strip(" ") == "":
                lines = lines[:-1]
            # 去除子块最后一行末尾的空白字符串
            # lines[-1] = lines[-1].rstrip()
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
                if line_index > 0 or ans_normal_block:
                    # 软回车标识
                    pre_str = t_num*'\t'+ "  "
                    # 匹配开头“\t\t  ”, 多个"\t", 两个空格
                    match = re.match(r'^\x20{0,}\t+\x20\x20', line)
                    if match is not None:
                        #统一先删除，后面再加上
                        line = line[len(match[0]):]
                elif line_index == 0:
                    pre_str = t_num*'\t'+ "- "

                #加上t_num*'\t'+ "  " 或者t_num*'\t'+ "- "
                processed_result.append(pre_str + line)
        return "\n".join(processed_result)

    def find_code_blocks(self, text):
        pattern = re.compile(r'```')
        matches = list(pattern.finditer(text))
        if len(matches) % 2 != 0:
            raise VisibleException("代码块没有正确闭合", status=400)
        pair_positions = []
        for i in range(0, len(matches), 2):
            pair_positions.append((matches[i].start(), matches[i+1].start()+3))
        return pair_positions
    
    def replace_error_tag_str(self, text):
        return text.replace('＃', '#')
    
    def replace_outside_code_blocks(self, text):
        code_blocks = self.find_code_blocks(text)
        # 找到所有 # 的位置
        # hash_positions = [m.start() for m in re.finditer(
        #     r'(\t{0,}-{0,}[\x20]{1,})(#{1,}[\x20]{1,})', text)]
        hash_positions = [(m.start(), m.end())for m in re.finditer(
            r'#{1,}[\x20]{1,}', text)]
        if hash_positions and hash_positions[0][0]==0:
            hash_positions = hash_positions[1:]

        # 初始化新文本
        new_text = list(text)
        for pos_start, pos_end in hash_positions:
            # 检查 # 是否在任何一个代码块内
            if not any(start <= pos_start < end for start, end in code_blocks):
                # 如果不在代码块内，替换为 @
                new_text[pos_start:pos_end] = '@'*(pos_end - pos_start - 1) + " "
        # 返回新文本
        return ''.join(new_text)

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
        djfsfjsfjds;
        ```
        生成效果：
        ```
        - ## 2023/5/14 07:11:00:
        \t- TODO sdfjslfjds
        djfsfjsfjds;
        ```        
        """
        title_string = "##"
        tag_string = "#"
        block_pre_string = ["- ", "\t- "]
        normal_parse_list = [
            ('- ', '\t- ')
        ]
        # 替换规则, 类似的字符串上下顺序有要求，优先匹配的放上面
        list_parse_pre = [
            ('- ', '\t\t- '),
            ('@blk ', '\t- '),
            ('@blk- ', '\t\t\t- '),
            ('@blk-', '\t\t\t- '),
            ('@blk', '\t- '),
            ('@ans ', '\t-@ans '),
            ('@ans', '\t-@ans '),
        ]
        que_flag = False
        ans_flag = False
        que_condition_flag = 0
        ans_condition_flag = 0
        que_strings = ["#que", "\t- #que", "- #que"]
        ans_strings = ["#ans", "\t- #ans", "- #ans"]
        # normal_blk_strings = ["@blk ", "@blk"]

        todo_key = ["--todo ", "--TODO ",
                    "--done ", "--DONE "]
        todo_value = ["\t- TODO ", "\t- DONE "]
        todo_map = {todo_key[0]:todo_value[0],
                    todo_key[1]:todo_value[0],
                    todo_key[2]:todo_value[1],
                    todo_key[3]:todo_value[1]}
        content = self.replace_error_tag_str(content)
        content = self.replace_outside_code_blocks(content)
        content_list = content.split('\n')
        for i, content in enumerate(content_list):
            if i == 0 and content.strip()[:len(title_string)] == title_string:
                # 第一个时间戳标题需要设置为logseq最上层的子块，所以不带"\t"
                content_list[i] = block_pre_string[0] + content_list[i]

            # que_strings = ["#que ", "\t- #que", "- #que"]
            if not que_flag:
                content_strip_space = content.strip(' ')
                # match_list =[]
                for item in que_strings:
                    # matched = int(content_strip_space[:len(item)] == item)
                    # match_list.append(matched)
                    if content_strip_space[:len(item)] == item:
                        content = que_strings[0] + content[len(item):]
                        content_list[i] = content
                        que_condition_flag = True
                        break

            if not que_flag and content and que_condition_flag:
                que_flag = True
                up_line = i-1
                # 将上一行（带标签）当做子块
                up_line_list = content_list[up_line].strip()
                if up_line != 0 and content_list[up_line].startswith(block_pre_string[1]):
                    continue
                # 当遇到 ”- # tag1“
                if up_line != 0 and content_list[up_line].startswith(block_pre_string[0]):
                    content_list[up_line] = "\t" + content_list[up_line]
                    continue
                if up_line != 0 and up_line_list and up_line_list[0] == tag_string:
                    #给问题的上一行（标题）添加 前缀 `block_pre_string[1]`
                    content_list[up_line] = block_pre_string[1] + content_list[up_line]
                else:
                    content_list[i] = block_pre_string[1] + content_list[i]

            # 这一行将视为特殊标签，并作为子块
            # ans_strings = ["#ans", "\t- #ans", "- #ans"]
            if not ans_flag:
                content_strip_space = content.strip(' ')
                for item in ans_strings:
                    if content_strip_space[:len(item)] == item:
                        content = ans_strings[1] + content[len(item):]
                        content_list[i] = content
                        ans_flag = True
                        break
                for old, new in normal_parse_list:
                    if content.startswith(old):
                        content = new + content[len(old):]
                        content_list[i] = content
                        break

            # 解析`-todo ` 变为子块
            if content and (content.strip()[:len(todo_key[0])] in todo_map
                            or content.strip() in todo_map):
                new_content = todo_map[content.strip()[:len(todo_key[0])]] + content[
                    len(todo_key[0]):]
                content_list[i] = new_content

            # 解析`- ` 变为子块, ans_flag = True, ensure right place. "\t- #ans" will not match this condition
            if ans_flag and content:
                for old, new in  list_parse_pre:
                    if content.startswith(old):
                        content = new + content[len(old):]
                        content_list[i] = content
                        break

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
        FLOMO_API_URL = CONF.diary_log['FLOMO_API_URL']
        post_data = { "content": "Hello, #flomo https://flomoapp.com" }
        requests.post(FLOMO_API_URL, json=post_data)

    def send_log_flomo(self, flomo_post_data):
        FLOMO_API_URL = CONF.diary_log['FLOMO_API_URL']
        requests.post(FLOMO_API_URL, json=flomo_post_data)

    # 向notion发送信息
    def send_log_notion(self, diary_log):
        return notion_api.create_database_page(CONF.diary_log['NOTION_API_KEY'],
                                                CONF.diary_log['DATABASE_ID'],
                                                diary_log)

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

    # 同步任务，批量获取 github 文件内容
    def get_contents_from_github(self, token, repo, sync_file_path_list,
                                 branch_name):
        contents = self.driver.get_contents_from_github(
            token, repo,
            sync_file_path_list,
            branch_name)
        return contents

    def sync_files_to_card_contents(
            self,
            github_access_info,
            user_settings
            ):
        """_summary_

        Args:
            github_access_info (_type_): _description_

        Returns:
            dict:: {str: list(tuple(str, str))}
        """

        current_sync_file = user_settings['current_sync_file']
        other_sync_file_list = user_settings['other_sync_file_list']
        # if current_sync_file and other_sync_file_list:

        other_sync_file_list = [path.strip() for path in
                            other_sync_file_list.split(',')] \
            if other_sync_file_list else []

        sync_file_paths = [current_sync_file.strip()] + \
            other_sync_file_list

        access_token = github_access_info['access_token']
        # repo = CONF.diary_log['GITHUB_REPO']
        repo = github_access_info['github_repo_name']
        # if not (repo and access_token):
        #     return []
        branch_name = "main"

        contents = self.get_contents_from_github(
            access_token, repo, sync_file_paths, branch_name)
        if len(contents.keys()) != len(sync_file_paths):
            LOG.warn("contents length and len(sync_file_paths) not equal")

        # diary_table_name = user_info['diary_table_name']
        # processed_card_contents = {}
        sync_files_to_card_contents = []
        for sync_file in contents:
            processed_card_contents = self.driver.text_to_card_contents(
                content=contents[sync_file])
            sync_files_to_card_contents.append((sync_file, processed_card_contents))
        return sync_files_to_card_contents

    # def sync_contents_from_github_to_db(self, sync_file_paths, sync_table_names):
    #     if len(sync_file_paths) != len(sync_table_names):
    #         raise Exception("sync_file_paths and sync_table_names length not equal")
    #     token = CONF.diary_log['GITHUB_TOKEN']
    #     repo = CONF.diary_log['GITHUB_REPO']
    #     branch_name = "main"
    #     contents = self.get_contents_from_github(
    #         token, repo, sync_file_paths, branch_name)
    #     if len(contents.keys()) != len(sync_file_paths):
    #         LOG.warn("contents length and len(sync_file_paths) not equal")
    #     # sync contents to db
    #     path_table_map = dict(zip(sync_file_paths, sync_table_names))
    #     # sync_table_names = [path_table_map[file_path] for file_path in contents]
    #     for file_path in contents:
    #         self.sync_contents_to_db(
    #             [contents[file_path]],
    #             table_name=path_table_map[file_path],
    #             data_base_path=SYNC_DATA_BASE_PATH)

    def sync_contents_from_jianguoyun_to_db(
            self, sync_file_paths, sync_table_names):
        if len(sync_file_paths) != len(sync_table_names):
            raise Exception("sync_file_paths and sync_table_names length not equal")
        JIANGUOYUN_COUNT = CONF.api_conf.JIANGUOYUN_COUNT
        JIANGUOYUN_TOKEN = CONF.api_conf.JIANGUOYUN_TOKEN
        base_url = CONF.api_conf.base_url


        contents = self.get_contents_from_jianguoyun(
            base_url, JIANGUOYUN_COUNT, JIANGUOYUN_TOKEN, sync_file_paths)
        if len(contents.keys()) != len(sync_file_paths):
            LOG.warn("contents length and len(sync_file_paths) not equal")
        # sync contents to db
        path_table_map = dict(zip(sync_file_paths, sync_table_names))
        # sync_table_names = [path_table_map[file_path] for file_path in contents]
        for file_path in contents:
            self.sync_contents_to_db(
                [contents[file_path]],
                table_name=path_table_map[file_path],
                data_base_path=SYNC_DATA_BASE_PATH)

    def get_card_contents_from_jianguoyun(
            self, access_data: Dict,
            user_settings: Dict):
        acount = access_data['jianguoyun_account']
        token = access_data['jianguoyun_token']

        current_sync_file = user_settings['current_sync_file']
        other_sync_files = user_settings['other_sync_file_list']
        other_sync_file_list = [path.strip() for path in
                            other_sync_files.split(',')] \
            if other_sync_files else []
        sync_file_paths = [current_sync_file.strip()] + \
            other_sync_file_list

        sync_files_to_contents: Dict = self.driver.\
            get_contents_from_jianguoyun(
            acount, token, sync_file_paths)

        if len(sync_files_to_contents.keys()) != len(sync_file_paths):
            LOG.warn("contents length and len(sync_file_paths) not equal")

        card_contents = [
            (sync_file,
            self.driver.text_to_card_contents(
                    content=sync_files_to_contents[sync_file]))
            for sync_file in sync_files_to_contents
        ]
        return card_contents

    # sync contents to database
    def sync_contents_to_db(self, contents, table_name, data_base_path):
        self.driver.sync_contents_to_db(contents, table_name, data_base_path)


    # s is input text
    def normalize_text(self, s):
        BLOCK_SEPARATOR = r'\t+-\s'
        s = re.sub(BLOCK_SEPARATOR, "", s).strip()
        s = re.sub(r'@blk',  ' ', s).strip()
        s = re.sub(r'\s+',  ' ', s).strip()
        # s = re.sub(r". ,","",s)
        # remove all instances of multiple spaces
        s = s.replace("\n", "")
        s = s.replace("..",".")
        s = s.replace(". .",".")
        s = s.strip()

        return s

    def get_que_string_from_content(self, content: str) -> List[str]:
        """get que  content

        Args:
            content (string): diary content

        Returns:
            List[str]
        """
        # "#s?que" 匹配 "#que" "#sque"
        separators = ["#s?que", "#ans"]
        result = []
        # 匹配标签，找到所有的标签
        if re.search(separators[0], content):
            content_split_0_list = re.split(f"({separators[0]})", content)
            for i in range(2, len(content_split_0_list), 2):
                content_split_1_list = re.split(f"({separators[1]})",
                                                    content_split_0_list[i])
                result.append(self.normalize_text(content_split_1_list[0]))
        return result

    def get_all_que_from_contents(self, contents: List[str]) -> List[str]:
        """get all que string from contents

        Args:
            contents (List[str]): contents

        Returns:
            List[str]: que string list
        """
        que_string_list = []
        index = []
        for i, content in enumerate(contents):
            ques= self.get_que_string_from_content(content)
            for que in ques:
                que_string_list.append(que)
                index.append(i)
        return index, que_string_list

@dependency.provider('diary_db_api')
class DiaryDBManager(manager.Manager):
    driver_namespace = "memoflow.app.diary_log.driver"

    def __init__(self):
        super(DiaryDBManager, self).__init__(CONF.diary_log.DIARY_DB_DRIVER)

        # #debug need to delete
        # from memoflow.driver.sqlite3_db.diary_log import DBSqliteDriver
        # self.driver = DBSqliteDriver()
        self.sync_data_base_path = CONF.diary_log['SYNC_DATA_BASE_PATH']
        self.jianguoyun_access_table=CONF.diary_log[
            'JIANGUOYUN_ACCESS_TABLE_NAME']

    def add_user(self, username, password, salt, email=None):
        """
        Add a user to the file sync system.

        Args:
            username (str): The user's username.
            password (str): The user's password.
            email (str): The user's email address.

        Returns:
            None
        """
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']

        user_id = str(uuid.uuid4())
        diary_table_name = username_to_table_name(
            user_id=user_id,
            username=username)

        self.driver.add_user(
            user_id=user_id,
            username=username,
            password=password,
            salt=salt,
            email=email,
            diary_table_name=diary_table_name,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=USER_TABLE_NAME)

    def update_users_field(self,
                       user_id,
                       **field_dict,
                       ):
        self.driver.update_users_field(
            user_id=user_id,
            field_dict=field_dict,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=USER_TABLE_NAME
        )

    def create_diary_table(
            self,
            diary_table_name
            ):
        self.driver.create_diary_log_table(
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=diary_table_name
        )

    def user_add_or_update_github_access_data_to_db(
            self, user_id,
            data_dict,
            ):
        """
        Add GitHub access information for a user to the file sync system.

        Args:
            user_id (str): The ID of the user.
            data_dict (dict): The GitHub access information.

        Returns:
            None
        """
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        GITHUB_ACCESS_TABLE_NAME=CONF.diary_log['GITHUB_ACCESS_TABLE_NAME']

        self.driver.user_add_or_update_github_access_data(
            user_id=user_id,
            data_dict=data_dict,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=GITHUB_ACCESS_TABLE_NAME)

    def user_add_or_update_jianguoyun_access_data_to_db(
            self, user_id,
            data_dict,
            ):
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        # GITHUB_ACCESS_TABLE_NAME=CONF.diary_log['GITHUB_ACCESS_TABLE_NAME']
        JIANGUOYUN_ACCESS_TABLE=CONF.diary_log['JIANGUOYUN_ACCESS_TABLE_NAME']
        self.driver.user_add_or_update_data_to_db(
            user_id=user_id,
            data_dict=data_dict,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=JIANGUOYUN_ACCESS_TABLE)

    def get_jianguoyun_access_data_by_user_id(
            self, user_id):
        return self.driver.get_record_by_filters(
            filters={"user_id" : user_id},
            data_base_path=self.sync_data_base_path,
            table_name=self.jianguoyun_access_table
            )

    def user_partial_update_github_access_data_to_db(
            self, update_values, conditions):
        """更新表中的数据。函数接受更新的参数以及更新条件作为输入，
        然后执行相应的 SQL 语句来更新表

        Args:
            update_values (dict): 需要更新的字段
            conditions (dict): 更新的筛选条件, must contain `user_id`
        """
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        GITHUB_ACCESS_TABLE_NAME=CONF.diary_log['GITHUB_ACCESS_TABLE_NAME']
        self.driver.user_partial_update_github_access_data_to_db(
            update_values=update_values,
            conditions=conditions,
            table_name=GITHUB_ACCESS_TABLE_NAME,
            data_base_path=SYNC_DATA_BASE_PATH
            )

    def get_github_access_info_by_user_id(self, user_id):
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        GITHUB_ACCESS_TABLE_NAME = CONF.diary_log['GITHUB_ACCESS_TABLE_NAME']
        github_access_info = self.driver.get_github_access_info_by_user_id(
            user_id=user_id,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=GITHUB_ACCESS_TABLE_NAME)
        return github_access_info

    def get_user_info_by_username(self, username):
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']
        user_id = self.driver.get_user_info_by_username(
            username=username,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=USER_TABLE_NAME)
        return user_id

    def get_user_info_by_id(self, user_id):
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']
        user_info = self.driver.get_user_info_by_id(
            user_id=user_id,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=USER_TABLE_NAME)
        return user_info

    def update_user_settings_to_db(
            self, user_id:str, user_settings:dict) -> None:
        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        USER_SETTINGS_TABLE_NAME = CONF.diary_log['USER_SETTINGS_TABLE_NAME']

        self.driver.update_user_settings_to_db(
            user_id=user_id,
            user_settings=user_settings,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=USER_SETTINGS_TABLE_NAME)

    def get_user_settings(
            self,
            user_id: str) -> dict:

        SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
        USER_SETTINGS_TABLE_NAME = CONF.diary_log['USER_SETTINGS_TABLE_NAME']
        user_settings = self.driver.get_user_settings(
            user_id=user_id,
            data_base_path=SYNC_DATA_BASE_PATH,
            table_name=USER_SETTINGS_TABLE_NAME
            )
        for key, value in user_settings.items():
            if value.strip().lower() == 'true':
                user_settings[key] = True
            if value.strip().lower() == 'false':
                user_settings[key] = False

        return user_settings


    def add_log(self,
                user_id,
                content,
                tags,
                sync_file=None,
                # jianguoyun_sync_file=None,
                data_base_path=SYNC_DATA_BASE_PATH
                ):
        """save diary(content, tags) to table

        Args:
            content (string): 笔记内容
            tags (list): 笔记的标签，例如：[a,b,c]
        """

        # user_info = self.get_user_info_by_id(
        #     user_id=user_id)
        table_name = self.driver.get_table_name_by_user_id(user_id)
        tags_string = ','.join(tags)
        record_id = self.driver.inser_diary_to_table(
            content=content,
            tags=tags_string,
            table_name=table_name,
            data_base_path=data_base_path,
            sync_file=sync_file,
            # jianguoyun_sync_file=jianguoyun_sync_file,
            )
        return record_id

    def insert_batch_records(
            self,
            user_id,
            columns,
            records,
            data_base_path=SYNC_DATA_BASE_PATH
            ):
        table_name = self.driver.get_table_name_by_user_id(user_id)
        self.driver.insert_batch_records(
            columns=columns,
            records=records,
            table_name=table_name,
            data_base_path=data_base_path)

    def update_log(self,
                   id,
                   user_id,
                   content,
                   tags,
                   data_base_path=SYNC_DATA_BASE_PATH):
        """update diary log

        Args:
            id (int): diary log id
            content (string): diary log content
            tags (list): diary log tags
            data_base_path (string, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.
        """
        table_name = self.driver.get_table_name_by_user_id(user_id)
        tags_string = ','.join(tags)
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_data_dict = {'content': content,
                            'tags': tags_string,
                            'update_time': update_time,
                            }

        self.driver.update_log_to_table(
            id=id,
            update_data_dict=update_data_dict,
            table_name=table_name,
            data_base_path=data_base_path)
        return id

    def get_log_by_id(self,
                      user_id,
                      id,
                      columns=['content'],
                      data_base_path=SYNC_DATA_BASE_PATH):
        """get diary log by id

        Args:
            id (int): diary log id
            columns (list, optional): _description_. Defaults to ['contents'].
            data_base_path (string, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.

        """
        table_name = self.driver.get_table_name_by_user_id(user_id)
        row = self.driver.get_log_by_id(id=id,
                                        table_name=table_name,
                                        columns=columns,
                                        data_base_path=data_base_path)
        return row

    def get_all_logs(self,
                 user_id,
                 columns=['content'],
                 data_base_path=SYNC_DATA_BASE_PATH):
        """get all diary logs

        Args:
            columns (list, optional): _description_. Defaults to ['contents'].
            data_base_path (string, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.

        """

        user_info = self.get_user_info_by_id(
            user_id=user_id)
        diary_table_name = user_info['diary_table_name']
        rows = self.driver.get_all_logs(table_name=diary_table_name,
                                        columns=columns,
                                        data_base_path=data_base_path)
        return rows

    def get_logs_by_filters(self,
                           user_id,
                           filters={},
                           columns=['content'],
                           order_by="create_time",
                           ascending=False,
                           page_size=None,
                           page_number=None,
                           data_base_path=SYNC_DATA_BASE_PATH
                           ):
        """get logs by filter

        Args:
            columns (list, optional): _description_. Defaults to ['contents'].
            data_base_path (string, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.

        Returns:
            string: json string
        """
        table_name = self.driver.get_table_name_by_user_id(user_id)
        rows = self.driver.get_logs_by_filters(
            filters=filters,
            columns=columns,
            order_by=order_by,
            ascending=ascending,
            page_size=page_size,
            page_number=page_number,
            table_name=table_name,
            data_base_path=data_base_path)
        return rows

    def delete_log(self,
                  id,
                  user_id,
                  data_base_path=SYNC_DATA_BASE_PATH):
        """delete one diary log

        Args:
            id (int): diary log id
            data_base_path (string, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.
        """

        table_name = self.driver.get_table_name_by_user_id(user_id)
        return self.driver.delete_log(
            id=id,
            table_name=table_name,
            data_base_path=data_base_path)

    def delete_records_not_in_list(
            self,
            user_id,
            field_name,
            values_to_keep,
            data_base_path=SYNC_DATA_BASE_PATH):
        """Based on a certain field, delete all records whose value is not in the given list

        Args:
            field_name (str): _description_
            values_to_keep (list): _description_
            data_base_path (str, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.
        """
        table_name = self.driver.get_table_name_by_user_id(user_id)
        self.driver.delete_records_not_in_list(
            table_name=table_name,
            field_name=field_name,
            values_to_keep=values_to_keep,
            data_base_path=data_base_path)

    def delete_log_by_filters(
            self,
            user_id,
            filters,
            data_base_path=SYNC_DATA_BASE_PATH
            ):

        table_name = self.driver.get_table_name_by_user_id(user_id)
        self.driver.delete_records_by_filters(
            table_name=table_name,
            filters=filters,
            data_base_path=data_base_path)

    def delete_all_log(self,
                       table,
                       data_base_path=SYNC_DATA_BASE_PATH,
                       ):
        """delete all diary logs of one table

        Args:
            data_base_path (string, optional): 数据库地址. Defaults to SYNC_DATA_BASE_PATH.
            table (string, optional): 表名
        """

        self.driver.delete_all_log(table_name=table,
                                   data_base_path=data_base_path)

    # review provider
    def get_review_logs(self, table, columns, data_base_path):
        """get all diary logs

        Args:
            table (string, optional): _description_ 
            columns (list, optional): _description_. Defaults to ['contents'].
            data_base_path (string, optional): _description_. Defaults to SYNC_DATA_BASE_PATH.

        Returns:
            string: json string
        """
        rows = self.driver.get_all_logs(table_name=table,
                                         columns=columns,
                                         data_base_path=data_base_path)
        contents = [row[0] for row in rows]
        return json.dumps({'logs': contents})

    def delete_all_review_log(self, data_base_path, table):
        """delete all diary logs of one table

        Args:
            data_base_path (string, optional): 数据库地址. Defaults to SYNC_DATA_BASE_PATH.
            table (string, optional): 表名.
        """
        self.driver.delete_all_log(table_name=table, data_base_path=data_base_path)

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
        rows = self.driver.get_all_logs(table_name, columns, data_base_path)

        contents = [row[0] for row in rows]
        return json.dumps({'logs': contents})

    def save_log_to_clipboard_table(
            self, table_name, data_dict, data_base_path):
        self.driver.insert_columns_to_table(
            table_name=table_name,
            data_dict=data_dict,
            data_base_path=data_base_path)
