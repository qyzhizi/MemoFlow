from celery import Celery

from web_dl.conf import CONF
from web_dl.app.diary_log.driver import notion_api

CELERY_BROKER_URL='redis://localhost:6379'
CELERY_RESULT_BACKEND='redis://localhost:6379'

celery = Celery(__name__,
                broker=CELERY_BROKER_URL,
                backend=CELERY_BROKER_URL)

@celery.task
def celery_send_log_notion(diary_log):
    return notion_api.create_database_page(CONF.diary_log['notion_api_key'],
                                           CONF.diary_log['database_id'],
                                           diary_log['content'])
