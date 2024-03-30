# coding=utf-8
from collections import OrderedDict
import io
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


class JianGuoYunClient(object):

    def __init__(self, base_url: str, acount: str, token: str) -> None:
        self.client = Client(base_url=base_url, auth=(acount, token))
        self.file_exists = {}

    def exists(self, path:str) -> bool:
        if self.file_exists.get(path, None) is None:
            res = self.client.exists(path=path)
            self.file_exists[path] = res
            return res
        else:
            return self.file_exists[path]
    
    def upload_content_to_new_file(self, content: str, to_path: str,
                                   overwrite: bool = False,
                                   encoding='utf-8') -> None:
        if not self.client.exists(to_path):
            file_obj = io.BytesIO(content.encode(encoding))
            self.client.upload_fileobj(file_obj, to_path, overwrite)
            # 创建新文件后，更新file_exists，否者后续一直认为该文件不存在
            self.file_exists[to_path] = to_path


    def add_content_to_file(self, added_content: str, file_path: str, mode: str = 'r',
                    encoding='utf-8'):
        with self.client.open(path=file_path, mode=mode, encoding=encoding) as file:
            content = file.read()
            updated_content = added_content + "\n" + content
        updated_file_obj = io.BytesIO(updated_content.encode(encoding))
        self.client.upload_fileobj(updated_file_obj, file_path, overwrite=True)
    
    def update_whole_file(self, updated_content: str, file_path: str,
                          encoding='utf-8'):
        file_obj = io.BytesIO(updated_content.encode(encoding))
        self.client.upload_fileobj(file_obj, file_path, overwrite=True)
    
    def get_file_content(self, path: str, encoding='utf-8'):
        if self.exists(path):
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
    def __init__(self, base_url, token, max_size):
        super().__init__(max_size)
        self.base_url = base_url
        self.token = token

    def get_client(self, jianguoyun_account):
        client = self.get(jianguoyun_account)
        if client is None:
            client = JianGuoYunClient(self.base_url, jianguoyun_account, self.token)
            self.put(jianguoyun_account, client)
        return client