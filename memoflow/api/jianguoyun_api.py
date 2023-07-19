# coding=utf-8
import io
from webdav4.client import Client

from memoflow.conf import CONF

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
    