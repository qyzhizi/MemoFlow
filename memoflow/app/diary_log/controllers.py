#!/usr/bin/env python
# coding=utf-8
# import asyncio
import base64
import logging
import json
from datetime import datetime
from datetime import timedelta
from webob.exc import HTTPUnauthorized
from webob.exc import HTTPFound
from webob import Response
from webob import exc
from github.GithubException import UnknownObjectException
from github.GithubException import BadCredentialsException

from memoflow.conf import CONF
from memoflow.core import wsgi
from memoflow.core import dependency
from memoflow.utils.token_jwt import token_required
from memoflow.app.diary_log.common import GithubTablePathMap
from memoflow.app.diary_log.common import JianguoyunTablePathMap
# from memoflow.app.diary_log import common
from memoflow.utils.common import validate_linux_file_path
from memoflow.utils.common import validate_gitrepo_path
from memoflow.utils import common as utils_common
from memoflow.exception.visiable_exc import VisibleException, VisibleResponse

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

SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
SYNC_TABLE_NAME = CONF.diary_log['SYNC_TABLE_NAME']
REVIEW_TABLE_NAME = CONF.diary_log['REVIEW_TABLE_NAME']

#clipboard
CLIPBOARD_TABLE_NAME = CONF.diary_log['CLIPBOARD_TABLE_NAME']  #clipboard数据表名
CLIPBOARD_DATA_BASE_PATH = CONF.diary_log[
    'DATA_BASE_CLIPBOARD_PATH']  #clipboard数据库路径

# GitHub App
CLIENT_SECRET = CONF.diary_log['CLIENT_SECRET']
CLIENT_ID = CONF.diary_log['CLIENT_ID']
GITHUB_APP_URL = CONF.diary_log['GITHUB_APP_URL']

if CONF.diary_log['SEND_TO_GITHUB'] == True:
    sync_file_paths = GithubTablePathMap.sync_file_paths
    sync_table_names = GithubTablePathMap.sync_table_names
elif CONF.diary_log['SEND_TO_JIANGUOYUN'] == True:
    sync_file_paths = JianguoyunTablePathMap.sync_file_paths
    sync_table_names = JianguoyunTablePathMap.sync_table_names

@dependency.requires('diary_log_api')
# @dependency.requires('llm_api')
@dependency.requires('vector_db_api')
@dependency.requires('diary_db_api')
@dependency.requires('asyn_task_api')
class DiaryLog(wsgi.Application):
    
    # #debug
    # def __init__(self):
    #     from memoflow.app.diary_log.provider import Manager
    #     from memoflow.app.diary_log.provider import DiaryDBManager
    #     self.diary_log_api = Manager()
    #     self.diary_db_api = DiaryDBManager()

    def register(self, req):
        data = json.loads(req.body)
        username = data.get('username', None)
        password = data.get('password', None)
        if not username or not password:
            raise VisibleException("Username or Password is Null !", status=400)
        
        # hashed_password, salt
        hashed_password, base64_salt = utils_common.hash_password(password)

        email = data.get('email', None)
        user_info = self.diary_db_api.get_user_info_by_username(username)
        if user_info:
            return Response(json.dumps({"error": "User already exists"}))

        self.diary_db_api.add_user(
            username, hashed_password, base64_salt, email)

        user_info = self.diary_db_api.get_user_info_by_username(username)
        LOG.info(f"user diary_table_name: "
                 f"{user_info['diary_table_name']}"
                 f"user id: {user_info['id']}"
                 )
        self.diary_db_api.create_diary_table(
            diary_table_name=user_info['diary_table_name'])

        response = Response(json.dumps({"register_success": 1}))
        return response

    def login(self, req):

        ''' 处理获取的json数据 '''
        # 从请求中获取POST数据, 并转换为JSON格式
        data = json.loads(req.body)
        username = data.get('username', None)
        password = data.get('password', None)
        if not username or not password:
            raise VisibleException("Username or Password is Null !", status=400)
        LOG.info(f"user: { username} login")

        ''' 从数据库获取用户数据, 并验证哈希后密码是否匹配 '''
        user_info = self.diary_db_api.get_user_info_by_username(
            username)  # 从数据库中获取的用户信息
        if not user_info:
            # response = Response(json.dumps({"error": "Invalid credentials"}))
            # response.status_code = 401  # 设置状态码为 401
            # return response
            raise VisibleException(f"User: {username} not exist !")
        hashed_password, _ = utils_common.hash_password(
            password=password , 
            salt=user_info['salt'])

        user_name_db = user_info.get("username", None)
        password_db = user_info.get("password", None)
        if username and password and (username == user_name_db and
            hashed_password == password_db):
            token = self.diary_log_api.generate_token(user_info['id'])

            # 创建响应对象
            response = Response(json.dumps({"token": token}))
            # 设置名为 "user_id" 的 Cookie，值为用户ID
            response.set_cookie('Authorization', 'Bearer ' + token)

            return response
        else:
            raise VisibleException(
                f"User: {username} not exist or Password not correct!")

        return response
    
    def logout(self, req):
        ''' 清除用户身份验证信息并注销会话 '''
        # 获取请求中的 Cookie
        cookies = req.cookies

        # 检查是否存在名为 "Authorization" 的 Cookie
        if 'Authorization' in cookies:
            # 创建响应对象
            response = Response()

            # 清除名为 "Authorization" 的 Cookie
            response.delete_cookie('Authorization')

            # 可选：将用户从任何其他会话数据中注销，如数据库中的活动会话表

            # 返回注销成功的响应
            return response
        else:
            # 如果用户尚未登录，返回错误响应
            return Response("User not logged in", status=401)
    
    # @token_required
    # def set_user_avatar(self, req):
    #     # 检查是否有上传的文件
    #     if 'image' not in req.POST:
    #         raise VisibleException("No image uploaded.", status=400)

    #     # 获取上传的文件
    #     image_file = req.POST['image'].file
    #     image_data = common.validate_image(image_file)
    #     user_id = req.environ['user_id']
    #     self.diary_db_api.update_users_field(
    #         user_id=user_id,
    #         avatar_image=image_data)

    @token_required
    def set_user_account_info(self, req):
        data = json.loads(req.body)
        username = data.get('username', None)
        email = data.get('email', None)
        avatar_string = data.get('image', None)
        field_dict = {}
        if username:
            field_dict['username'] = username
        if avatar_string is not None:
            field_dict['avatar_image'] = avatar_string
        if email is not None:
            field_dict['email'] = email

        # # 检查是否有上传的文件
        # if 'image' not in req.POST:
        #     raise VisibleException("No image uploaded.", status=400)

        # 获取上传的文件
        # image_file = req.POST['image'].file
        # image_data = common.validate_image(image_file)
        user_id = req.environ['user_id']
        self.diary_db_api.update_users_field(
            user_id=user_id,
            **field_dict)
    
    @token_required
    def set_user_password_info(self, req):
        data = json.loads(req.body)
        password = data.get('new_password', None)
        repeat_password = data.get('repeat_password', None)
        if password != repeat_password:
             raise VisibleException("Passwords do not match!", status=400)
        
        # hashed_password, salt
        hashed_password, base64_salt = utils_common.hash_password(password)

        field_dict = {}
        if password:
            field_dict['password'] = hashed_password
            field_dict['salt'] = base64_salt
        user_id = req.environ['user_id']
        self.diary_db_api.update_users_field(
            user_id=user_id,
            **field_dict)

    @token_required
    def get_user_avatar_image(self, req):
        user_id = req.environ['user_id']
        user_info = self.diary_db_api.get_user_info_by_id(
            user_id=user_id)
        # 已经是 Base64编码的字符串
        avatar_image = user_info.get('avatar_image', None)
        # 将字节流转换为Base64编码的字符串
        # if avatar_image:
        #     base64_data = base64.b64encode(avatar_image).decode('utf-8')
        return {
        "username" : user_info.get('username', None),
        "avatar_image" : avatar_image 
        }

    @token_required
    def get_user_account_info(self, req):
        user_id = req.environ['user_id']
        user_info = self.diary_db_api.get_user_info_by_id(
            user_id=user_id)
        # 已经是 Base64编码的字符串
        avatar_image = user_info.get('avatar_image', None)
        return {
        "username" : user_info.get('username', None),
        "email" : user_info.get('email', None),
        "avatar_image" : avatar_image,
        }

    @token_required
    def add_log(self, req):
        # 从请求中获取POST数据
        data = req.body
        user_id = req.environ['user_id']
        current_sync_file = None
        # jianguoyun_sync_file = None
        

        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log json_data:, %s" % diary_log["content"][:70])

        # get tags
        tags = self.diary_log_api.get_tags_from_content(diary_log['content'])
        # 处理卡片笔记
        processed_content = self.diary_log_api.process_content(
            diary_log['content'])
        processed_block_content = self.diary_log_api.process_block(
            processed_content)


        # # 发送到浮墨笔记
        # flomo_post_data = {"content": processed_content}
        # self.diary_log_api.send_log_flomo(flomo_post_data)

        # # 向notion 发送数据
        # self.asyn_task_api.celery_send_log_notion(diary_log=processed_content)
        # # asyncio.run(self.diary_log_api.run_tasks(diary_log))

        # get user settings
        user_settings = self.diary_db_api.get_user_settings(user_id)
        try:
            # 向github仓库（logseq 笔记软件）发送数据
            if user_settings.get('SEND_TO_GITHUB', None) == True:

                github_access_info = self.get_access_token_by_user_id(
                    user_id=user_id)
                if github_access_info is None:
                    return json.dumps({"error": "no github access token"})
                current_sync_file = user_settings['current_sync_file']
                # file_path = CONF.diary_log['GITHUB_CURRENT_SYNC_FILE_PATH']
                # file_path = CURRENT_SYNC_FILE
                commit_message = "commit by memoflow"
                branch_name = "main"
                # token = CONF.diary_log['GITHUB_TOKEN']
                token = github_access_info['access_token']

                # repo = CONF.diary_log['GITHUB_REPO']
                repo = github_access_info['github_repo_name']
                added_content = processed_block_content
                self.asyn_task_api.celery_update_file_to_github(
                    token, repo, current_sync_file, added_content, commit_message,
                    branch_name)
        except Exception as e:
            LOG.error(e)

        # 向坚果云发送异步任务，更新文件
        # 坚果云账号
        try:
            if user_settings.get('SEND_TO_JIANGUOYUN', None) == True:

                jianguoyun_access_data = self.diary_db_api.\
                    get_jianguoyun_access_data_by_user_id(
                    user_id=user_id)
                
                added_content = processed_block_content
                self.asyn_task_api.celery_update_file_to_jianguoyun(
                    acount=jianguoyun_access_data['jianguoyun_account'],
                    token=jianguoyun_access_data['jianguoyun_token'],
                    to_path=user_settings['current_sync_file'],
                    content=added_content,
                    overwrite=True)
                current_sync_file = user_settings['current_sync_file']
        except Exception as e:
            LOG.error(e)

        # 保存到本地数据库
        record_id = self.diary_db_api.add_log(
            user_id,
            processed_block_content,
            tags,
            sync_file=current_sync_file,
            # jianguoyun_sync_file= current_sync_file
            )

        # save que string to vector db
        que_string: List[str] = self.diary_log_api.get_que_string_from_content(
            processed_block_content)
        if que_string:
            self.asyn_task_api.asyn_add_texts_to_vector_db_coll(
                texts=que_string,
                metadatas=[{
                    "user_id": user_id,
                    "id":record_id,
                    "tags":
                    ','.join(tags)
                }])

        return json.dumps(
            {"record_id": record_id, "content": processed_block_content})

    @token_required
    def get_logs(self, req):
        user_id = req.environ['user_id']

        # 获取page_size和page_number参数
        page_size = int(req.GET.get('page_size', 30))
        page_number = int(req.GET.get('page_number', 1))

        contents = []
        ids = []
        rows = self.diary_db_api.get_logs_by_filter(
            user_id=user_id,
            columns=['content', 'id'],
            order_by="create_time",
            ascending=False,
            page_size=page_size,
            page_number=page_number
        )

        contents.extend([row[0] for row in rows])
        ids.extend([row[1] for row in rows])
        return json.dumps({'logs': contents, 'ids': ids,
                           'page_size': page_size,
                           'page_number': page_number})

    @token_required
    def update_log(self, req):
        # 从请求中获取POST数据
        data = req.body
        user_id = req.environ['user_id']

        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log json_data:, %s" % diary_log["content"][:70])

        # get tags
        tags = self.diary_log_api.get_tags_from_content(diary_log['content'])
        # 处理卡片笔记
        processed_content = self.diary_log_api.process_content(
            diary_log['content'])
        processed_block_content = self.diary_log_api.process_block(
            processed_content)
        old_diary_content = self.diary_db_api.get_log_by_id(
            user_id=user_id,
            id=diary_log["record_id"],
            columns=['content', 'sync_file'])
        # get sync_file
        sync_file = old_diary_content[1]

        # 保存到本地数据库
        self.diary_db_api.update_log(
            id = diary_log["record_id"],
            user_id = user_id,
            content = processed_block_content,
            tags = tags,
            )

        que_strings: str = self.diary_log_api.get_que_string_from_content(
            processed_block_content)
        que_string = que_strings[0] if que_strings else None

        old_que_strings: str = self.diary_log_api.get_que_string_from_content(
            old_diary_content[0])
        old_que_string = old_que_strings[0] if old_que_strings else None

        # 异步更新 `que_string` 到向量数据库
        self.asyn_update_que_string_to_vector_db_coll(
            user_id, old_que_string, que_string, tags)

        # 向远程仓库发送更新后的 sync_file
        self.asyn_push_user_current_sync_file_to_repo(
            user_id=user_id,
            sync_file=sync_file)

        return json.dumps({"content": processed_block_content})

    @token_required
    def delete_log(self, req, record_id):
        user_id = req.environ['user_id']
        old_diary_content = self.diary_db_api.get_log_by_id(
            user_id=user_id,
            id=record_id,
            columns=['content', 'sync_file'])
        
        # get sync_file
        sync_file = old_diary_content[1]

        # delete que string in verctor db
        where = {"$and":[{'id': record_id}, {'user_id': user_id}]}
        self.vector_db_api.delete_items_by_metadata_filters(
            where=where,
        )

        res = self.diary_db_api.delete_log(user_id=user_id, id=record_id)
        if res:
            LOG.info(f"delete diary log success, id: {record_id}")

        user_settings = self.diary_db_api.get_user_settings(user_id)
        updated_contents = None
        # 向github仓库（logseq 笔记软件）发送更新后的数据
        if user_settings.get('SEND_TO_GITHUB', None) == True:
            # file_path = CONF.diary_log['GITHUB_CURRENT_SYNC_FILE_PATH']
            github_access_info = self.get_access_token_by_user_id(
                user_id=user_id)
            # default order_by create_time DESC descending sort
            rows = self.diary_db_api.get_logs_by_filter(
                user_id=user_id,
                filter={"sync_file": sync_file},
                columns=['content'],
                order_by="create_time",
                ascending=False
            )
            updated_contents = [row[0] for row in rows]
            updated_contents = "\n".join(updated_contents)

            file_path = sync_file
            commit_message = "commit by memoflow"
            branch_name = "main"
            # token = CONF.diary_log['GITHUB_TOKEN']
            token = github_access_info['access_token']
            repo = github_access_info['github_repo_name']
            # repo = CONF.diary_log['GITHUB_REPO']

            self.asyn_task_api.celery_push_updatedfile_to_github(
                token, repo, file_path, updated_contents, commit_message,
                branch_name)
            
        if user_settings.get('SEND_TO_JIANGUOYUN', None) == True:
            jianguoyun_access_data = self.diary_db_api.\
                get_jianguoyun_access_data_by_user_id(
                user_id=user_id)
            # jianguoyun_sync_file = jianguoyun_access_data['current_sync_file']
            if user_settings.get('SEND_TO_GITHUB', None) != True \
                or not updated_contents:
                rows = self.diary_db_api.get_logs_by_filter(
                    user_id=user_id,
                    filter={"sync_file": sync_file},
                    columns=['content'],
                    order_by="create_time",
                    ascending=False
                )
                updated_contents = [row[0] for row in rows]
                updated_contents.reverse()
                updated_contents = "\n".join(updated_contents)
            self.asyn_task_api.celery_push_updatedfile_to_jianguoyun(
                acount=jianguoyun_access_data['jianguoyun_account'],
                token=jianguoyun_access_data['jianguoyun_token'],
                to_path=sync_file,
                content=updated_contents)

        # res = self.diary_db_api.delete_log(user_id=user_id, id=record_id)
        # if res:
        #     LOG.info(f"delete diary log success, id: {record_id}")

    def delete_all_log(self, req):
        return self.diary_db_api.delete_all_log()

    def test_flomo(self, req):
        self.diary_log_api.test_post_flomo()
        return "sucess"

    # review
    @token_required
    def get_review_logs(self, req):
        return self.diary_db_api.get_review_logs(
            table=REVIEW_TABLE_NAME,
            columns=['content'],
            data_base_path=SYNC_DATA_BASE_PATH)

    @token_required
    def delete_all_review_log(self, req):
        return self.diary_db_api.delete_all_review_log(
            data_base_path=SYNC_DATA_BASE_PATH, table=REVIEW_TABLE_NAME)

    # clipboard
    @token_required
    def get_clipboard_logs(self, req):
        return self.diary_db_api.get_clipboard_logs(
            table_name=CLIPBOARD_TABLE_NAME,
            columns=['content'],
            data_base_path=CLIPBOARD_DATA_BASE_PATH)

    def clipboard_addlog(self, req):
        # 从请求中获取POST数据
        data = req.body
        # 将POST数据转换为JSON格式
        diary_log = json.loads(data)
        LOG.info("diary_log json_data:, %s" % diary_log["content"][:70])
        # 保存到本地数据库
        self.diary_db_api.save_log_to_clipboard_table(
            table_name=CLIPBOARD_TABLE_NAME,
            data_dict={'content':diary_log["content"]},
            data_base_path=CLIPBOARD_DATA_BASE_PATH)
        return json.dumps(diary_log)  # data 是否可行？

    # @token_required
    # def get_contents_from_github(self, req):
    #     user_id = req.environ['user_id']
    #     user_settings = self.diary_db_api.get_user_settings(user_id)
    #     if user_settings.get('SEND_TO_GITHUB', None) != True:
    #         return json.dumps({"error": "CONF SEND_TO_GITHUB != True"})
    #     if len(sync_file_paths) != len(sync_table_names):
    #         raise Exception("sync_file_paths and sync_table_names length not equal")
    #     github_access_info = self.get_access_token_by_user_id(
    #             user_id=user_id)
    #     # token = CONF.diary_log['GITHUB_TOKEN']
    #     token = github_access_info['access_token']
    #     repo = github_access_info['github_repo_name']
    #     # token = CONF.diary_log['GITHUB_TOKEN']
    #     # repo = CONF.diary_log['GITHUB_REPO']
    #     branch_name = "main"
    #     contents = self.diary_log_api.get_contents_from_github(
    #         token, repo, sync_file_paths, branch_name)
    #     if len(contents) != len(sync_file_paths):
    #         raise Exception("contents length and len(sync_file_paths) not equal")
    #     result = []
    #     for content in contents:
    #         result.extend(content)
    #     # return contents
    #     return json.dumps({"contents": result})

    @token_required
    def sync_contents_from_repo_to_db(self, req):
        user_id = req.environ['user_id']
        user_settings = self.diary_db_api.get_user_settings(user_id)
        columns = ['content', 'tags', 'sync_file']
        records = []
        sync_files_to_card_contents = []

        self.diary_db_api.delete_records_not_in_list(
            user_id=user_id,
            field_name='sync_file',
            values_to_keep=['']
        )

        if user_settings.get('SEND_TO_GITHUB', None) == True:
            github_access_info = self.get_access_token_by_user_id(
                user_id=user_id)

            sync_files_to_card_contents = \
                self.diary_log_api.sync_files_to_card_contents(
                github_access_info=github_access_info,
                user_settings=user_settings,
                )
        elif user_settings.get('SEND_TO_JIANGUOYUN', None) == True:
            jianguoyun_access_data = self.diary_db_api.\
                    get_jianguoyun_access_data_by_user_id(
                    user_id=user_id)
            
            sync_files_to_card_contents = self.diary_log_api.\
                get_card_contents_from_jianguoyun(
                access_data = jianguoyun_access_data,
                user_settings=user_settings,
                )
        for sync_file, card_contents in sync_files_to_card_contents[::-1]:
            if not card_contents:
                continue
            for content, tags in card_contents:
                records.append([content, tags, sync_file])

        self.diary_db_api.insert_batch_records(
            user_id=user_id,
            columns=columns,
            records=records,
        )
        return "success"


    @token_required
    def search_contents_from_vecter_db(self, req):
        user_id = req.environ['user_id']
        data = req.body
        # Convert post data to json format
        search_data = json.loads(data)['search_data']
        LOG.info("search_data json_data:, %s" % search_data)
        # search contents from vecter db
        search_result = []
        if search_data:
            filter = {"user_id": user_id}
            search_result = self.vector_db_api.get_similarity_search_docs(
                query=search_data, top_k=10, filter=filter)
        return json.dumps({"search_result": search_result})

    @token_required
    def update_all_que_to_vector_db(self, req):
        user_id = req.environ['user_id']
        # get logs and send all que string to vector db
        log_list = self.diary_db_api.get_all_logs(
                user_id=user_id, columns=['id', 'content', 'tags'])

        contents = [log[1] for log in log_list]
        index, que_list = self.diary_log_api.get_all_que_from_contents(
            contents)
        slice_log_list = [log_list[i] for i in index]
        tags = [log[2] for log in slice_log_list]
        # convert id into str
        ids = [str(log[0]) for log in slice_log_list]

        self.vector_db_api.delete_items_by_metadata_filters(
            where={"user_id":user_id})

        self.vector_db_api.add_texts(
            texts=que_list,
            metadatas=[{
                "user_id":user_id,
                "tag": tag,
                "id": id
            } for tag, id in zip(tags, ids)]
        )

        return "success"

    def peek_vector_db(self, req, limit):
        # peek vector db
        result_object = self.vector_db_api.peek_collection(limit=int(limit))
        result = {
            "ids": result_object.get('ids', None),
            "embeddings": result_object.get('embeddings', None),
            "metadatas": result_object.get('metadatas', None)
        }
        return json.dumps(result)

    def get_collection_items(self, req, limit: str):
        result_object = self.vector_db_api.get_collection_items(
            limit=int(limit))
        result = {
            "ids": result_object.get('ids', None),
            "embeddings": result_object.get('embeddings', None),
            "metadatas": result_object.get('metadatas', None)
        }
        return json.dumps(result)

    def get_vector_db_coll_all_ids(self, req):
        result_object = self.vector_db_api.get_vector_db_coll_all_ids()
        collection_size = self.vector_db_api.get_collection_size()
        result = {
            "ids": result_object.get('ids', None),
            "collection_size": collection_size
        }
        return json.dumps(result)

    @token_required
    def delete_collection_item(self, req):
        data = req.body
        # 将POST数据转换为JSON格式, ids 是列表
        ids: List = json.loads(data).get('ids', None)
        LOG.info("delete_data json_data:, %s" % ids)
        # delete collection item
        self.vector_db_api.delete_items_by_ids(ids=ids)
        return "success"
    
    @token_required
    def set_user_sync_files(self, req):
        user_id = req.environ['user_id']
        data = json.loads(req.body)
        current_sync_file = data.get('CurrentSyncFileName', None).strip()
        other_sync_file_list = data.get('OtherSyncFilesName', None).strip()

        other_sync_file_list = \
            [path.strip() for path in other_sync_file_list.split(',') 
             if path.strip()] if other_sync_file_list else []
        
        # delete Duplicate items
        if current_sync_file in other_sync_file_list:
            other_sync_file_list.remove(current_sync_file)
        
        # validate path
        try:
            validate_linux_file_path(current_sync_file)
            for sync_file in other_sync_file_list:
                    validate_linux_file_path(sync_file)
        except VisibleException as e:
            return VisibleResponse(str(e), status=400)

        other_sync_file_list = ','.join(other_sync_file_list)

        self.diary_db_api.update_user_settings_to_db(
                    user_id=user_id,
                    user_settings={
                        "current_sync_file": current_sync_file,
                        "other_sync_file_list": other_sync_file_list
                    })
        return Response(json.dumps({
            "success": 1,}))
    
    @token_required
    def get_user_sync_files(self, req):
        user_id = req.environ['user_id']
        user_settings = self.diary_db_api.get_user_settings(user_id)
        return Response(json.dumps({
            "success": 1,
            "current_sync_file": user_settings.get(
                'current_sync_file', None),
            "other_sync_file_list": user_settings.get(
                'other_sync_file_list', None)
            }))



    @token_required
    def delete_all_collection_item(self, req):
        all_collection_ids: List = self.\
            vector_db_api.get_vector_db_coll_all_ids().get(
            'ids', None)
        if all_collection_ids:
            self.vector_db_api.delete_items_by_ids(ids=all_collection_ids)
        return "success"

    @token_required
    def github_authenticate(self, req):
        github_auth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
        # 创建一个 HTTPFound 对象来重定向到 GitHub 授权链接
        response = HTTPFound(location=github_auth_url)
        return response

    @token_required
    def github_authenticate_callback(self, req):
        # 获取 GitHub 授权码
        code = req.GET.get('code')
        # 在这里对 code 进行处理
        if not code:
            return Response("No GitHub code found, github authenticate failed")

        # 调用 GitHub API 获取 access token
        origin_github_tokens_info = self.diary_log_api.get_access_token(code)
        user_id = req.environ['user_id']

        github_tokens_info = self.diary_log_api.\
                    process_github_tokens_info_to_db_format(
                        origin_github_tokens_info)

        # github_access_info = {
        #     'username': None,
        # }
        # github_access_info.update(github_tokens_info)

        self.diary_db_api.user_add_or_update_github_access_data_to_db(
            user_id, github_tokens_info)

        access_token_expires_at = github_tokens_info\
            ['access_token_expires_at'].strftime("%Y-%m-%d %H:%M:%S")
        refresh_token_expires_at = github_tokens_info\
        ['refresh_token_expires_at'].strftime("%Y-%m-%d %H:%M:%S")

        return Response(json.dumps({
            "success:": 1,
            "access_token_expires_at": access_token_expires_at,
            "refresh_token_expires_at": refresh_token_expires_at
            }))

    @token_required
    def github_app_authenticate(self, req):
        github_app_url = GITHUB_APP_URL
        # 创建一个 HTTPFound 对象来重定向到 GitHub 授权链接
        response = HTTPFound(location=github_app_url)
        return response
    
    @token_required
    def github_config(self, req):
        user_id = req.environ['user_id']
        data = req.body
        # 将POST数据转换为JSON格式
        config_data  = json.loads(data)
        config_input_repo_info = {
            "github_repo_name": config_data.get('gitRepPath', None).strip()
        }
                # validate path
        try:
            validate_gitrepo_path(
                config_input_repo_info['github_repo_name']
                )
        except VisibleException as e:
            return VisibleResponse(str(e), status=400)
        
        user_settings = self.diary_db_api.get_user_settings(user_id)

        github_repo_name = config_input_repo_info.get("github_repo_name", None)
        current_sync_file = user_settings.get("current_sync_file", None)

        # process other_sync_file_list to right format
        other_sync_file_list:str = user_settings.get(
            "other_sync_file_list", None)
        other_sync_file_list = \
            [path.strip() for path in other_sync_file_list.split(',') 
             if path.strip()] if other_sync_file_list else []
        # delete Duplicate items
        if current_sync_file in other_sync_file_list:
            other_sync_file_list.remove(current_sync_file)
        other_sync_file_list = ','.join(other_sync_file_list)
        
        # config_input_repo_info["current_sync_file"] = current_sync_file
        # config_input_repo_info["other_sync_file_list"] = other_sync_file_list

        # try:
        github_access_info = self.get_access_token_by_user_id(
            user_id=user_id)
        # except Exception as e:
            # return VisibleResponse(str(e), status=500)
        if not github_access_info:
            return VisibleResponse("github connect failed, try again later", status=500)
        access_token = github_access_info.get('access_token', None)

        config_input_flag = (github_repo_name !='') and (current_sync_file != '') 
                             
        status_dict ={
            "success": None,
            "config_input_flag": config_input_flag,
            "test_github_access": None,
            "unknown_object_exception": None,
            "bad_credentials_exception":None,
            "gitRepPath": config_data.get('gitRepPath', None),
            "gitCurrentSyncFileName": config_data.get(
                'gitCurrentSyncFileName', None),
            "gitOtherSyncFileName": config_data.get(
                'gitOtherSyncFileName', None)
            }

        self.diary_db_api.user_add_or_update_github_access_data_to_db(
            user_id=user_id,
            data_dict=config_input_repo_info)
        if  config_input_flag and access_token:
            try:

                # self.diary_log_api.init_sync_files_for_github(
                #     access_token=access_token,
                #     github_repo_name=github_repo_name,
                #     current_sync_file=current_sync_file,
                #     other_sync_file_list=other_sync_file_list)

                repo_name, owner =self.diary_log_api.test_github_access(
                    access_token=access_token,
                    github_repo_name=github_repo_name
                )
                assert repo_name and owner, 'github access failed'

                # bing github success , save flag to db
                self.diary_db_api.update_user_settings_to_db(
                    user_id=user_id,
                    user_settings={"SEND_TO_GITHUB": "True"})

                status_dict['success'] = 1
                status_dict['access_token_flg'] = 1
                status_dict['init_sync_files_for_github'] = 1
            except UnknownObjectException as e:
                LOG.error(e)
                status_dict['success'] = 0
                status_dict['unknown_object_exception'] = 1
            except BadCredentialsException as e:
                LOG.error(e)
                status_dict['success'] = 0
                status_dict['bad_credentials_exception'] = 1
            except  Exception as e:
                # ReadTimeout
                # BadCredentialsException 401
                # github.GithubException.UnknownObjectException 404
                LOG.error(e)
                status_dict['success'] = 0
                status_dict['init_sync_files_for_github'] = 0
        else:
            self.diary_db_api.update_user_settings_to_db(
                    user_id=user_id,
                    user_settings={"SEND_TO_GITHUB": "False"})
            status_dict['success'] = 0
            if not access_token:
                status_dict['access_token_flg'] = 0
            if not status_dict['config_input_flag']:
                status_dict['config_input_flag'] = 0

        return Response(json.dumps(status_dict))

    @token_required
    def jianguoyun_config(self, req):
        user_id = req.environ['user_id']
        data = req.body
        # 将POST数据转换为JSON格式
        config_data  = json.loads(data)
        config_input_jianguoyun = {
            "jianguoyun_account": config_data.get(
                'jianguoyun_account', None).strip(),
            "jianguoyun_token": config_data.get(
                'jianguoyun_token', None).strip(),
        }
        status_dict = {
            'success': None,
        }
        user_settings = self.diary_db_api.get_user_settings(user_id)
        current_sync_file = user_settings.get('current_sync_file', None)
        # other_sync_file_list = user_settings.get('other_sync_file_list', None)

        # current_sync_file = config_input_jianguoyun.get(
        #     "current_sync_file", None)
        # other_sync_file_list:str = config_input_jianguoyun.get(
        #     "other_sync_file_list", None)

        # other_sync_file_list = \
        #     [path.strip() for path in other_sync_file_list.split(',') 
        #      if path.strip()] if other_sync_file_list else []
                
        # delete Duplicate items
        # if current_sync_file in other_sync_file_list:
        #     other_sync_file_list.remove(current_sync_file)
        # other_sync_file_list = ','.join(other_sync_file_list)

        # config_input_jianguoyun["current_sync_file"] = current_sync_file
        # config_input_jianguoyun["other_sync_file_list"] = other_sync_file_list
        
        if config_input_jianguoyun['jianguoyun_account'] == '' or \
        config_input_jianguoyun['jianguoyun_token'] == '' or \
            current_sync_file == '':
            self.diary_db_api.update_user_settings_to_db(
                user_id=user_id,
                user_settings={"SEND_TO_JIANGUOYUN": 'False'})
            LOG.warn("jianguoyun configs is missing , "
                    "Please check you configrations")
            if current_sync_file == '':
                status_dict['current_sync_file_flag'] = 0
            if config_input_jianguoyun['jianguoyun_account'] == '':
                status_dict['jianguoyun_account'] = 0
            if config_input_jianguoyun['jianguoyun_token'] == '':
                status_dict['jianguoyun_token'] = 0


        self.diary_db_api.user_add_or_update_jianguoyun_access_data_to_db(
            user_id=user_id,
            data_dict=config_input_jianguoyun)

        jianguoyun_account = config_input_jianguoyun['jianguoyun_account']
        jianguoyun_token = config_input_jianguoyun['jianguoyun_token']

        # current_sync_file = user_settings['current_sync_file']
        # other_sync_file_list = user_settings['other_sync_file_list']

        # self.diary_log_api.init_sync_files_for_jianguoyun(
        #             jianguoyun_account=jianguoyun_account,
        #             jianguoyun_token=jianguoyun_token,
        #             current_sync_file=current_sync_file,
        #             other_sync_file_list=other_sync_file_list)  
        
        test_res = self.diary_log_api.test_jianguoyun_access(
            jianguoyun_account=jianguoyun_account,
            jianguoyun_token=jianguoyun_token
        )
        if not  test_res:
            LOG.info("jianguoyun access failed")
            status_dict['test_jianguoyun_access'] = 0

        else:
            self.diary_db_api.update_user_settings_to_db(
                        user_id=user_id,
                        user_settings={"SEND_TO_JIANGUOYUN": "True"})
            status_dict['success'] = 1
        
        return Response(json.dumps(status_dict))

    @token_required
    def get_github_config(self, req):
        user_id = req.environ['user_id']
        github_access_info = self.get_access_token_by_user_id(
            user_id=user_id)
        config_input_repo_info = {
            "github_repo_name": github_access_info.get('github_repo_name', None)
        }
        return Response(json.dumps({
            "success": 1,
            "gitRepPath": config_input_repo_info.get('github_repo_name', None)
            }))

    @token_required
    def get_jianguoyun_account(self, req):
        user_id = req.environ['user_id']
        try:
            jianguoyun_account_info = self.diary_db_api.\
                get_jianguoyun_access_data_by_user_id(user_id)
        except Exception as e:
            jianguoyun_account_info = {}
        config_info = {
            "jianguoyun_account": jianguoyun_account_info.get(
            'jianguoyun_account', None),
            "jianguoyun_token": jianguoyun_account_info.get(
                'jianguoyun_token', None)
        }

        return Response(json.dumps(config_info))


    def get_access_token_by_user_id(self, user_id):
        """ get github access info by user_id from db.
        if access_token has expired, get new access_token from github.
        if refresh_token has expired, return empty dict.
        if access_token and refresh_token both has expired, return empty dict.
        

        Args:
            user_id (uuid): _description_

        Returns:
            dict : github access info 
        """
        github_access_info = self.diary_db_api.\
            get_github_access_info_by_user_id(user_id)

        # access_token = github_access_info['access_token']
        refresh_token = github_access_info.get('refresh_token', None)
        access_token_expires_at = github_access_info.get(
            'access_token_expires_at', None)
        access_token_expires_at = datetime.strptime\
            (access_token_expires_at, '%Y-%m-%d %H:%M:%S.%f') \
                if access_token_expires_at else None
        
        if not refresh_token or not access_token_expires_at:
            LOG.error( "github refresh token don't exit, "
                    "please bing github again")
            raise Exception("github refresh token don't exit, "
                    "please bing github again")

        # 获取当前时间
        current_datetime = datetime.now()
        # if access_token hans expired
        if current_datetime > access_token_expires_at:
            LOG.info("access_token has expired")
            refresh_token_expires_at = github_access_info[
                'refresh_token_expires_at']
            refresh_token_expires_at = datetime.strptime\
                    (refresh_token_expires_at,
                    '%Y-%m-%d %H:%M:%S.%f')
            # if refresh token alse has expired
            if current_datetime > refresh_token_expires_at:
                LOG.error( "github refresh token has expired, \
                    please bing github again")
                raise Exception("github refresh token has expired, \
                    please bing github again")

            # 获取新的access_token
            try:
                origin_github_tokens_info = self.diary_log_api.\
                    get_github_access_token_by_refresh_token\
                    (refresh_token=refresh_token)
            except Exception as e:
                raise VisibleException(str(e), status=500)

            # update the new access_token to db
            processed_github_access_info = self.diary_log_api.\
                process_github_tokens_info_to_db_format(
                    origin_github_tokens_info)
            update_values = {
                'access_token': processed_github_access_info['access_token'],
                'access_token_expires_at': \
                    processed_github_access_info['access_token_expires_at'],
                'refresh_token': processed_github_access_info['refresh_token'],
                'refresh_token_expires_at': \
                    processed_github_access_info['refresh_token_expires_at'],
            }
            conditions = {'user_id': user_id}
            self.diary_db_api.\
                user_partial_update_github_access_data_to_db\
                      (update_values=update_values,
                        conditions=conditions)
            # update github_access_info dict
            github_access_info.update(update_values)
        return github_access_info

    def asyn_push_user_current_sync_file_to_repo(
            self, user_id, sync_file):
        user_settings = self.diary_db_api.get_user_settings(user_id)
        rows = None
        updated_content = None
        if user_settings.get('SEND_TO_GITHUB', None) == True:
            github_access_info = self.get_access_token_by_user_id(
                user_id=user_id)

            # default order_by create_time DESC descending sort
            rows = self.diary_db_api.get_logs_by_filter(
                user_id=user_id,
                filter={"sync_file": sync_file},
                columns=['content'],
                order_by="create_time",
                ascending=False
            )
            updated_contents = [row[0] for row in rows]
            # updated_contents.reverse()
            updated_content = "\n".join(updated_contents)
            file_path = sync_file
            commit_message = "commit by memoflow"
            branch_name = "main"
            token = github_access_info['access_token']

            # repo = CONF.diary_log['GITHUB_REPO']
            repo = github_access_info['github_repo_name']

            self.asyn_task_api.celery_push_updatedfile_to_github(
                token, repo, file_path, updated_content, commit_message,
                branch_name)
        # elif CONF.diary_log['SEND_TO_JIANGUOYUN'] == True:
        if user_settings.get('SEND_TO_JIANGUOYUN', None) == True:
            # table_name = JianguoyunTablePathMap.current_table_name
            jianguoyun_access_data = self.diary_db_api.\
                    get_jianguoyun_access_data_by_user_id(
                    user_id=user_id)
            # jianguoyun_sync_file = jianguoyun_access_data['current_sync_file']

            # table_path_of_repo = JianguoyunTablePathMap.current_table_path
            # other_table_path_map = JianguoyunTablePathMap.other_table_path_map
            if user_settings.get('SEND_TO_GITHUB', None) != True \
                or not updated_content:
                rows = self.diary_db_api.get_logs_by_filter(
                    user_id=user_id,
                    filter={"sync_file": sync_file},
                    columns=['content'],
                    order_by="create_time",
                    ascending=False
                )
                updated_contents = [row[0] for row in rows]
                # updated_contents.reverse()
                updated_content = "\n".join(updated_contents)
            self.asyn_task_api.celery_push_updatedfile_to_jianguoyun(
                jianguoyun_access_data['jianguoyun_account'],
                jianguoyun_access_data['jianguoyun_token'],
                sync_file,
                updated_content)

    def asyn_update_que_string_to_vector_db_coll(
            self, user_id, old_que_string, que_string, tags):

        update_flag = que_string != old_que_string

        metadatas = [{"user_id": user_id, "tags": ','.join(tags)}]
        if update_flag and old_que_string:
            search_result = self.vector_db_api.similarity_search(
                    query=old_que_string, top_k=1)
            # document = search_result["document"][0]
            distance = search_result["distance"][0]
            if distance >= 0.1:
                update_flag = False
            # threshold = 0
            origin_id= search_result["id"][0]

        if update_flag and que_string and old_que_string:
            self.asyn_task_api.asyn_update_texts_to_vector_db_coll(
                ids=[origin_id],
                texts=[que_string],
                metadatas= metadatas)
        elif que_string and old_que_string is None:
            self.asyn_task_api.asyn_add_texts_to_vector_db_coll(
                texts=[que_string],
                metadatas=metadatas)
        elif que_string is None and old_que_string:
            self.vector_db_api.delete_items_by_ids(ids=[origin_id])
