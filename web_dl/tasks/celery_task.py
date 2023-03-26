from celery import Celery

from web_dl.conf import CONF
from web_dl.api import notion_api
from web_dl.api import github_api
from web_dl.api.jianguoyun_api import JianGuoYunClient
from web_dl.api.jianguoyun_api import jianguoyun_clients

CELERY_BROKER_URL='redis://localhost:6379'
CELERY_RESULT_BACKEND='redis://localhost:6379'

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
