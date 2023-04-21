from celery import Celery
import logging
import random

from web_dl.conf import CONF
from web_dl.api import notion_api
from web_dl.api import github_api
from web_dl.api.jianguoyun_api import JianGuoYunClient
from web_dl.api.jianguoyun_api import jianguoyun_clients
from web_dl.db import diary_log as diary_log_db

DIARY_LOG_TABLE = CONF.diary_log['diary_log_table']
REVIEW_DIARY_LOG = CONF.diary_log['review_diary_log']
TAGS = ["que", "ans", "dl"]
DATA_BASE_PATH = CONF.diary_log['data_base_path']

CELERY_BROKER_URL='redis://localhost:6379'
CELERY_RESULT_BACKEND='redis://localhost:6379'

LOG = logging.getLogger(__name__)

celery = Celery(__name__,
                broker=CELERY_BROKER_URL,
                backend=CELERY_BROKER_URL)

@celery.task
def celery_send_log_notion(diary_log):
    return notion_api.create_database_page(CONF.diary_log['notion_api_key'],
                                           CONF.diary_log['database_id'],
                                           diary_log)
github_api_instance ={}

@celery.task
def celery_update_file_to_github(token, repo, file_path, added_content,
                                 commit_message, branch_name):
    if github_api_instance.get(repo, None) is None:
        github_api_instance[repo] = github_api.GitHupApi(token=token, repo=repo)
    my_api_instance = github_api_instance[repo]
    return my_api_instance.update_file(file_path=file_path,
                                       added_content=added_content,
                                       commit_message=commit_message,
                                       branch_name=branch_name)

# 更新文件到坚果云
@celery.task
def update_file_to_janguoyun(base_url: str, acount: str, token: str,
                             to_path: str, content: str, overwrite: bool = True) -> None:
    if jianguoyun_clients.get(acount, None) is None:
        jianguoyun_clients[acount] = JianGuoYunClient(base_url, acount, token)
    my_client = jianguoyun_clients[acount]
    if my_client.exists(to_path):
        my_client.add_content_to_file(added_content=content, file_path=to_path)
    else:
        my_client.upload_content_to_new_file(content, to_path, overwrite)

@celery.task
def time_task():
    print("Running time task ...")

@celery.task
def time_get_diary_log_task():
    LOG.info("Running time_get_diary_log_task ...")
    rows=diary_log_db.get_rows_by_tags(table_name=DIARY_LOG_TABLE,
                                        tags=TAGS,
                                        data_base_path=DATA_BASE_PATH)
    random_row = random.choice(rows)
    LOG.info(f"random_row: {random_row}")
    # diary_log_db.inser_diary_to_table(table_name=REVIEW_DIARY_LOG,
    #                                   content=random_row[0],
    #                                   tags=random_row[1],
    #                                   data_base_path=DATA_BASE_PATH)
    

celery.conf.beat_schedule = {
    'run-every-12*60*60-seconds': {
        'task': 'web_dl.tasks.celery_task.time_task',
        'schedule': 12*60*60
    },
    'time_get_diary_log_task': {
    'task': 'web_dl.tasks.celery_task.time_get_diary_log_task',
    'schedule': 5
    }
}