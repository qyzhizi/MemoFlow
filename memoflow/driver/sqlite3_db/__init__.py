from memoflow.driver.sqlite3_db.diary_log import DBSqliteDriver as diary_log_db
from memoflow.conf import CONF
from memoflow.utils import common

SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
SYNC_TABLE_NAME = CONF.diary_log['SYNC_TABLE_NAME']
REVIEW_TABLE_NAME = CONF.diary_log['REVIEW_TABLE_NAME']

SECOND_SYNC_DATA_BASE_PATH =  CONF.diary_log_second['SYNC_DATA_BASE_PATH']
SECOND_SYNC_TABLE_NAME = CONF.diary_log_second['SYNC_TABLE_NAME']
# clipboard
#clipboard数据表名
CLIPBOARD_TABLE_NAME = CONF.diary_log['CLIPBOARD_TABLE_NAME'] 
#clipboard数据库路径
CLIPBOARD_DATA_BASE_PATH = CONF.diary_log['DATA_BASE_CLIPBOARD_PATH'] 

FILE_LIST = CONF.diary_log['GITHUB_CURRENT_SYNC_FILE_PATH'] + ',' \
            + CONF.diary_log['GITHUB_OTHER_SYNC_FILE_LIST']
_, sync_table_names = common.paths_to_table_names(FILE_LIST)

def init_db():
    diary_log_db.init_db_diary_log(data_base_path=SYNC_DATA_BASE_PATH,
                                table_name=SYNC_TABLE_NAME)
    # diary_log_second.init_db_diary_log_second(data_base_path=SECOND_DATA_BASE_PATH,
    #                                           table_name=SYNC_TABLE_NAME)
    diary_log_db.init_db_diary_log(data_base_path=SECOND_SYNC_DATA_BASE_PATH,
                                table_name=SECOND_SYNC_TABLE_NAME)
    diary_log_db.create_table(data_base_path=SYNC_DATA_BASE_PATH,
                           table_name=REVIEW_TABLE_NAME)
    for table_name in sync_table_names:
        diary_log_db.create_table(data_base_path=SYNC_DATA_BASE_PATH,
                                 table_name=table_name)
    diary_log_db.init_db_clipboard_log(
        data_base_path=CLIPBOARD_DATA_BASE_PATH,
        table_name=CLIPBOARD_TABLE_NAME)