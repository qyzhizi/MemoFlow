# coding=utf-8
from collections import OrderedDict
import io
import os
from webdav4.client import Client

from memoflow.conf import CONF
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
jianguoyun_clients = {}
JIANGUOYUN_BASE_URL = CONF.api_conf.base_url
JIANGUOYUN_PREFIX =  CONF.api_conf.jianguoyun_prefix


class JianGuoYunClient(object):

    def __init__(self, base_url: str, acount: str, token: str) -> None:
        self.client = Client(base_url=base_url, auth=(acount, token))
        # self.file_exists = {}

        # mkdir JIANGUOYUN_PREFIX path
        # if not self.client.exists(JIANGUOYUN_PREFIX):
        #     self.client.mkdir(JIANGUOYUN_PREFIX)

    def process_path(self, path):
        directory, filename = os.path.split(path)
        if not directory.startswith(JIANGUOYUN_PREFIX):
            directory = os.path.join(JIANGUOYUN_PREFIX, directory.lstrip('/'))
        dir_processed = '/'
        for dir_path in directory.split('/')[1:]:
            dir_processed = os.path.join(dir_processed, dir_path)
            if not self.client.exists(dir_processed):
                self.client.mkdir(dir_processed)
        return os.path.join(dir_processed, filename)

    # def process_path(self, path):
    #     directory, filename = os.path.split(path)
    #     if not directory.startswith(JIANGUOYUN_PREFIX):
    #         if not directory.startswith('/'):
    #             directory = '/' + directory 
    #         path = JIANGUOYUN_PREFIX + path
    #     if not self.client.exists(path):
    #         self.client.mkdir(path)
    #     return path + '/' + filename

    # def exists(self, path:str) -> bool:
    #     if self.file_exists.get(path, None) is None:
    #         res = self.client.exists(path=path)
    #         self.file_exists[path] = res
    #         return res
    #     else:
    #         return self.file_exists[path]
    
    def upload_content_to_new_file(self, content: str, to_path: str,
                                   overwrite: bool = False,
                                   encoding='utf-8') -> None:
        # to_path = self.process_path(to_path)
        if not self.client.exists(to_path):
            file_obj = io.BytesIO(content.encode(encoding))
            self.client.upload_fileobj(file_obj, to_path, overwrite)
            # 创建新文件后，更新file_exists，否者后续一直认为该文件不存在
            # self.file_exists[to_path] = to_path


    def add_content_to_file(
            self,
            added_content: str,
            file_path: str, mode: str = 'r', encoding='utf-8'):
        # file_path = self.process_path(file_path)
        with self.client.open(path=file_path, mode=mode, encoding=encoding) as file:
            content = file.read()
            updated_content = added_content + "\n" + content
        updated_file_obj = io.BytesIO(updated_content.encode(encoding))
        self.client.upload_fileobj(updated_file_obj, file_path, overwrite=True)
    
    def update_whole_file(self, updated_content: str, file_path: str,
                          encoding='utf-8', overwrite=True):
        # file_path = self.process_path(file_path)
        file_obj = io.BytesIO(updated_content.encode(encoding))
        self.client.upload_fileobj(file_obj, file_path, overwrite=overwrite)
    
    def get_file_content(self, path: str, encoding='utf-8'):
        # path = self.process_path(path)
        if self.client.exists(path):
            with self.client.open(path=path, mode='r', encoding=encoding) as file:
                return file.read()

    def get_contents(self, paths: List[str], encoding='utf-8'):
        """
        获取文件内容，返回字典，key为文件路径，value为文件内容
        :param paths: 文件路径列表
        :param encoding: 文件编码
        :return: {path: content}
        """
        contents = {}
        for path in paths:
            if not path:
                continue
            path = self.process_path(path)
            content = self.get_file_content(path, encoding)
            if content:
                contents[path] = content
        return contents


class LRUCache:
    def __init__(self, max_size):
        self.max_size = max_size
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = value


class JianGuoYunAccountManager(LRUCache):
    def __init__(self, max_size,
                 base_url=JIANGUOYUN_BASE_URL):
        super().__init__(max_size)
        self.base_url = base_url

    def get_client(self, token, acount):
        client = self.get(acount)
        if client is None:
            client = JianGuoYunClient(
                base_url=self.base_url, 
                acount=acount,
                token=token)
            self.put(acount, client)
        return client