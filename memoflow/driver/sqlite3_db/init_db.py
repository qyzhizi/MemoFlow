from memoflow.driver.sqlite3_db.diary_log import DBSqliteDriver as diary_log_db
from memoflow.conf import CONF
from memoflow.app.diary_log.common import GithubTablePathMap
from memoflow.app.diary_log.common import JianguoyunTablePathMap

SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
SYNC_TABLE_NAME = CONF.diary_log['SYNC_TABLE_NAME']
REVIEW_TABLE_NAME = CONF.diary_log['REVIEW_TABLE_NAME']
USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']
USER_SETTINGS_TABLE_NAME = CONF.diary_log['USER_SETTINGS_TABLE_NAME']
GITHUB_ACCESS_TABLE_NAME = CONF.diary_log['GITHUB_ACCESS_TABLE_NAME']

SECOND_SYNC_DATA_BASE_PATH =  CONF.diary_log_second['SYNC_DATA_BASE_PATH']
SECOND_SYNC_TABLE_NAME = CONF.diary_log_second['SYNC_TABLE_NAME']

#clipboard数据表名
CLIPBOARD_TABLE_NAME = CONF.diary_log['CLIPBOARD_TABLE_NAME'] 
#clipboard数据库路径
CLIPBOARD_DATA_BASE_PATH = CONF.diary_log['DATA_BASE_CLIPBOARD_PATH'] 

def init_db():
    diary_log_db.init_db_diary_log(data_base_path=SYNC_DATA_BASE_PATH)
    # diary_log_db.init_db_diary_log(data_base_path=SECOND_SYNC_DATA_BASE_PATH,
    #                             table_name=SECOND_SYNC_TABLE_NAME)
    diary_log_db.create_diary_log_table(
        data_base_path=SYNC_DATA_BASE_PATH,
        table_name=REVIEW_TABLE_NAME)

    # if user_settings.get('SEND_TO_GITHUB', None) == True:
    #     for table_name in GithubTablePathMap.sync_table_names:
    #         diary_log_db.create_diary_log_table(
    #             data_base_path=SYNC_DATA_BASE_PATH,
    #             table_name=table_name)
    # elif CONF.diary_log['SEND_TO_JIANGUOYUN'] == True:
    #     for table_name in JianguoyunTablePathMap.sync_table_names:
    #         diary_log_db.create_diary_log_table(
    #             data_base_path=SYNC_DATA_BASE_PATH,
    #             table_name=table_name)
    diary_log_db.init_db_clipboard_log(
        data_base_path=CLIPBOARD_DATA_BASE_PATH,
        table_name=CLIPBOARD_TABLE_NAME)
    
    diary_log_db.create_user_table(
        data_base_path=SYNC_DATA_BASE_PATH,
        user_table_name=CONF.diary_log['USER_TABLE_NAME'])
    diary_log_db.create_github_access_table(
        data_base_path=SYNC_DATA_BASE_PATH,
        user_table_name=CONF.diary_log['USER_TABLE_NAME'],
        github_access_table_name=CONF.diary_log['GITHUB_ACCESS_TABLE_NAME'])
    # create user_settings table
    diary_log_db.create_user_settings_table(
        data_base_path=SYNC_DATA_BASE_PATH,
        user_settings_table_name=CONF.diary_log['USER_SETTINGS_TABLE_NAME']
    )
    # create jianguoyun_access_table
    diary_log_db.create_jianguoyun_access_table(
        data_base_path=SYNC_DATA_BASE_PATH,
        user_table_name=CONF.diary_log['USER_TABLE_NAME'],
        jianguoyun_access_table_name=CONF.diary_log[
            'JIANGUOYUN_ACCESS_TABLE_NAME'])
