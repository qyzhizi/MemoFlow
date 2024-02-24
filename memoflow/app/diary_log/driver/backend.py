from memoflow.api.github_api import GitHupApi
from memoflow.api.jianguoyun_api import JianGuoYunClient
from memoflow.api.jianguoyun_api import jianguoyun_clients
import memoflow.app.diary_log.driver.sync_contents_to_db as db_sync
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

class DiaryLogDriver(object):
    def __init__(self, github_api_instance={},
                jianguoyun_clients=jianguoyun_clients) -> None:
        # save github api instance, if not exist, create one, else use it,
        # key is repo, value is GitHupApi instance, if instance number is too 
        # many, may cause memory leak。
        self.github_api_instance =github_api_instance
        self.azure_openai_embedding = None
        self.jianguoyun_clients = jianguoyun_clients

    def celery_update_file_to_github(self, token, repo, file_path, added_content,
                                    commit_message, branch_name):
        if self.github_api_instance.get(repo, None) is None:
            self.github_api_instance[repo] = GitHupApi(token=token, repo=repo)
        my_api_instance = self.github_api_instance[repo]
        my_api_instance.update_file(file_path=file_path,
                                    added_content=added_content,
                                    commit_message=commit_message,
                                    branch_name=branch_name)

    def get_contents_from_github(self, token, repo, sync_file_path_list,
                                 branch_name):
        if self.github_api_instance.get(repo, None) is None:
            self.github_api_instance[repo] = GitHupApi(token=token,
                                                       repo=repo)
        my_api_instance = self.github_api_instance[repo]
        contents = my_api_instance.get_contents(sync_file_path_list=sync_file_path_list,
                                            branch_name=branch_name)

        return contents
    
    def get_contents_from_jianguoyun(self, base_url: str, 
                                     acount: str,
                                     token: str,
                                     files_paths: List[str]):
        if self.jianguoyun_clients.get(acount, None) is None:
            jianguoyun_clients[acount] = JianGuoYunClient(base_url, acount, token)
        my_client = jianguoyun_clients[acount]
        return my_client.get_contents(files_paths)
    
    def sync_contents_to_db(self, contents, table_name, data_base_path):
        db_sync.process_file_content_2_db(contents=contents,
                                          table_name=table_name,
                                          data_base_path=data_base_path)

    