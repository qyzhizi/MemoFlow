from celery import Celery

from web_dl.conf import CONF
from web_dl.api import notion_api
from web_dl.api import github_api

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
def celery_update_file_to_github(token, repo, file_path, added_content, commit_message, branch_name):
    if not github_api_instance.get(repo,''):
        github_api_instance[repo] = github_api.GitHupApi(token=token, repo=repo)
    else:
        my_api_instance = github_api_instance[repo]
    return my_api_instance.update_file(file_path=file_path,
                                       added_content=added_content,
                                       commit_message=commit_message,
                                       branch_name=branch_name)
