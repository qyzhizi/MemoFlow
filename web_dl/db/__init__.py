from web_dl.db import diary_log
from web_dl.db import diary_log_lrx
from web_dl.conf import CONF

DATA_BASE_PATH = CONF.diary_log['data_base_path']
DIARY_LOG_TABLE = CONF.diary_log['diary_log_table']
REVIEW_DIARY_LOG = CONF.diary_log['review_diary_log_table']

def init_db():
    diary_log.init_db_diary_log(data_base_path=DATA_BASE_PATH, table_name=DIARY_LOG_TABLE)
    diary_log_lrx.init_db_diary_log_lrx()
    diary_log.create_table(data_base_path=DATA_BASE_PATH, table_name=REVIEW_DIARY_LOG)