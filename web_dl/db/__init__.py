from web_dl.db import diary_log
from web_dl.db import diary_log_lrx

def init_db():
    diary_log.init_db_diary_log()
    diary_log_lrx.init_db_diary_log_lrx()