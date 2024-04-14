# coding=utf-8
from memoflow.core import dependency
from memoflow.core import manager
from memoflow.conf import CONF
from memoflow.tasks import celery_task

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


@dependency.provider('asyn_task_api')
class AsynTaskManager(manager.Manager):
    driver_namespace = "memoflow.driver.driver_manager"

    def __init__(self):
        super(AsynTaskManager,
              self).__init__(CONF.driver_manager.ASYN_TASK_DRIVER)

    def asyn_add_texts_to_vector_db_coll(self,
                                    texts: List[str],
                                    metadatas: Optional[List[dict]] = None,
                                    ids: Optional[List[str]] = None):
        return self.driver.asyn_add_texts_to_vector_db_coll(texts,
                                                            metadatas,
                                                            ids)

    def asyn_update_texts_to_vector_db_coll(self,
                                    ids: List[str],
                                    texts: List[str],
                                    metadatas: Optional[List[dict]] = None,
                                    ):
        return self.driver.asyn_update_texts_to_vector_db_coll(
                                                        ids=ids, 
                                                        texts=texts,
                                                        metadatas= metadatas)

    # 向celery 发送异步任务
    def celery_send_log_notion(self, diary_log):
        return celery_task.celery_send_log_notion.delay(diary_log)

        # 向celery 发送异步任务
    def celery_update_file_to_github(self, token, repo, file_path,
                                     added_content, commit_message,
                                     branch_name):
        return celery_task.celery_update_file_to_github.delay(
            token, repo, file_path, added_content, commit_message, branch_name)
    
    def celery_push_updatedfile_to_github(self, token, repo, file_path,
                                          updated_content, commit_message,
                                          branch_name):
        return celery_task.celery_push_updatedfile_to_github.delay(
            token, repo, file_path, updated_content, commit_message, branch_name)
    
    def celery_push_updatedfile_to_jianguoyun(self,
                                              acount: str,
                                              token: str,
                                              to_path: str,
                                              content: str,
                                              ) -> None:
        celery_task.celery_push_updatedfile_to_jianguoyun.delay(
            acount, token, to_path, content)
        return None

    # 向坚果云发送异步任务，更新文件
    def celery_update_file_to_jianguoyun(self,
                                         acount: str,
                                         token: str,
                                         to_path: str,
                                         content: str,
                                         overwrite: bool = True) -> None:
        celery_task.update_file_to_janguoyun.delay(acount, token,
                                                   to_path, content, overwrite)
