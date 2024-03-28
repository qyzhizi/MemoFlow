import os
from oslo_config import cfg
from dotenv import dotenv_values
from memoflow.utils.common import filename_to_table_name

env_vars = dotenv_values(".env")

FLOMO_API_URL = env_vars.get("FLOMO_API_URL", None)

DATABASE_ID = env_vars.get("DATABASE_ID", None)
NOTION_API_KEY = env_vars.get("NOTION_API_KEY", None)

# github config
GITHUB_TOKEN = env_vars.get("GITHUB_TOKEN", None)
GITHUB_REPO = env_vars.get("GITHUB_REPO", None)
# github app config
CLIENT_SECRET = env_vars.get("CLIENT_SECRET", None)
CLIENT_ID = env_vars.get("CLIENT_ID", None)
GITHUB_APP_URL= env_vars.get("GITHUB_APP_URL", None)

GITHUB_CURRENT_SYNC_FILE_PATH = env_vars.get("GITHUB_CURRENT_SYNC_FILE_PATH",
                                             None)
JIANGUOYUN_CURRENT_SYNC_FILE_PATH = env_vars.get("JIANGUOYUN_CURRENT_SYNC_FILE_PATH",  None)                                             
GITHUB_OTHER_SYNC_FILE_LIST = env_vars.get("GITHUB_OTHER_SYNC_FILE_LIST", None)

# database cofig
SYNC_DATA_BASE_PATH = env_vars.get("SYNC_DATA_BASE_PATH", None)
SYNC_TABLE_NAME = env_vars.get("SYNC_TABLE_NAME", None)
REVIEW_TABLE_NAME = env_vars.get("REVIEW_TABLE_NAME", None)

DATA_BASE_CLIPBOARD_PATH = env_vars.get("DATA_BASE_CLIPBOARD_PATH", None)
CLIPBOARD_TABLE_NAME = env_vars.get("CLIPBOARD_TABLE_NAME", None)
DIARY_LOG_LOGIN_USER = env_vars.get("DIARY_LOG_LOGIN_USER", None)
DIARY_LOG_LOGIN_PASSWORD = env_vars.get("DIARY_LOG_LOGIN_PASSWORD", None)

USER_TABLE_NAME = env_vars.get("USER_TABLE_NAME", 'users')
USER_SETTINGS_TABLE_NAME = env_vars.get("USER_SETTINGS_TABLE_NAME",
                                        'user_settings')
GITHUB_ACCESS_TABLE_NAME = env_vars.get("GITHUB_ACCESS_TABLE_NAME",
                                        'github_access')
# jianguoyun db config
JIANGUOYUN_ACCESS_TABLE_NAME = env_vars.get("JIANGUOYUN_ACCESS_TABLE_NAME",
                                        'jianguoyun_access')

#获取发送任务标志位
SEND_TO_GITHUB = bool(int(env_vars.get("SEND_TO_GITHUB", 0)))
SEND_TO_JIANGUOYUN = bool(int(env_vars.get("SEND_TO_JIANGUOYUN", 0)))

# 默认配置项
if GITHUB_CURRENT_SYNC_FILE_PATH == None:
    # github repo根目录下的memoflow_sync文件夹
    GITHUB_CURRENT_SYNC_FILE_PATH = "memoflow_sync/first_file.md"

if SYNC_DATA_BASE_PATH == None:
    # 当前工作目录下，db_data文件夹
    SYNC_DATA_BASE_PATH = os.path.join("db_data", "memoflow_sync_data.db")
if SYNC_TABLE_NAME == None:
    # get GITHUB_CURRENT_SYNC_FILE_PATH file name
    if SEND_TO_GITHUB:
        file_name = os.path.basename(GITHUB_CURRENT_SYNC_FILE_PATH).strip()
    elif SEND_TO_JIANGUOYUN:
        file_name = os.path.basename(JIANGUOYUN_CURRENT_SYNC_FILE_PATH).strip()

    if file_name == "":
        file_name = "sync_data"
    file_name = file_name.split(".")[0]
    # 当前工作目录下，db_data文件夹
    SYNC_TABLE_NAME = filename_to_table_name(file_name)

if REVIEW_TABLE_NAME == None:
    REVIEW_TABLE_NAME = "review_diary_log"

if DATA_BASE_CLIPBOARD_PATH == None:
    # 当前工作目录下，db_data文件夹
    DATA_BASE_CLIPBOARD_PATH = os.path.join("db_data", "clipboard_data.db")
if CLIPBOARD_TABLE_NAME == None:
    CLIPBOARD_TABLE_NAME = "clipboard_log"

# 声明配置项
CONF_OPTS = [
    # database config
    cfg.StrOpt('SYNC_DATA_BASE_PATH',
               default=SYNC_DATA_BASE_PATH,
               help='同步数据库的路径'),
    cfg.StrOpt('DIARY_LOG_LOGIN_USER', default=DIARY_LOG_LOGIN_USER, help='用户名'),
    cfg.StrOpt('DIARY_LOG_LOGIN_PASSWORD', default=DIARY_LOG_LOGIN_PASSWORD, help='密码'),
    cfg.StrOpt('SYNC_TABLE_NAME', default=SYNC_TABLE_NAME, help='同步数据库的表名'),
    cfg.StrOpt('REVIEW_TABLE_NAME', default=REVIEW_TABLE_NAME, help='review表'),
    # cfg.StrOpt('USER_TABLE_NAME', default=USER_TABLE_NAME, help='user表'),
    # cfg.StrOpt('GITHUB_ACCESS_TABLE_NAME', default=GITHUB_ACCESS_TABLE_NAME, help='github access表'),

    # database user table
    cfg.StrOpt('USER_TABLE_NAME', default=USER_TABLE_NAME, help='user表'),
    cfg.StrOpt('GITHUB_ACCESS_TABLE_NAME',
               default=GITHUB_ACCESS_TABLE_NAME,
               help='github access表'),
    cfg.StrOpt('USER_SETTINGS_TABLE_NAME',
               default=USER_SETTINGS_TABLE_NAME,
               help='user_settings table name'
               ),
    # database jianguoyun table config
    cfg.StrOpt('JIANGUOYUN_ACCESS_TABLE_NAME',
               default=JIANGUOYUN_ACCESS_TABLE_NAME,
               help='jianguoyun access table name'),

    cfg.StrOpt('REVIEW_TAGS', default='que,web', help='review 筛选标签'),
    cfg.StrOpt('FLOMO_API_URL', default=FLOMO_API_URL, help='flomo api url'),
    cfg.StrOpt('DATABASE_ID', default=DATABASE_ID, help='notion db id'),
    cfg.StrOpt('NOTION_API_KEY', default=NOTION_API_KEY,
               help='notion api key'),
    # github config
    cfg.StrOpt('GITHUB_TOKEN',
               default=GITHUB_TOKEN,
               help='github access token'),
    cfg.StrOpt("GITHUB_REPO", default=GITHUB_REPO, help='github repo'),
    # github app config
    cfg.StrOpt('CLIENT_SECRET',
               default=CLIENT_SECRET,
               help='github client secret'),
    cfg.StrOpt('CLIENT_ID',
               default=CLIENT_ID,
               help='github client id'),
    cfg.StrOpt('GITHUB_APP_URL',
               default=GITHUB_APP_URL,
               help='GITHUB APP URL'),
    cfg.StrOpt("GITHUB_CURRENT_SYNC_FILE_PATH",
               default=GITHUB_CURRENT_SYNC_FILE_PATH,
               help='GITHUB_CURRENT_SYNC_FILE_PATH'),
    cfg.StrOpt("GITHUB_OTHER_SYNC_FILE_LIST",
               default=GITHUB_OTHER_SYNC_FILE_LIST,
               help='GITHUB_OTHER_SYNC_FILE_LIST'),
    cfg.StrOpt("DATA_BASE_CLIPBOARD_PATH",
               default=DATA_BASE_CLIPBOARD_PATH,
               help='clipboard_log db file path'),
    cfg.StrOpt("CLIPBOARD_TABLE_NAME",
               default=CLIPBOARD_TABLE_NAME,
               help='clipboard_log table name'),
    # 发送任务标志位
    cfg.BoolOpt("SEND_TO_GITHUB",
                default=SEND_TO_GITHUB,
                help='clipboard_log table name'),
    cfg.BoolOpt("SEND_TO_JIANGUOYUN",
                default=SEND_TO_JIANGUOYUN,
                help='clipboard_log table name'),
    cfg.StrOpt('CHROMA_PERSIST_DIRECTORY',
               default='db_data/chroma_persist/diary_log_app',
               help='chroma_persist directory'),
    cfg.StrOpt('COLLECTION_NAME',
                default='diary_log_collection',
                help='chroma_persist collection name'),
               
]

driver = cfg.StrOpt(
    'driver',
    default='driver',
    help='The driver to use for memoflow.app.diary_log',
)

DIARY_DB_DRIVER = cfg.StrOpt(
    'DIARY_DB_DRIVER',
    default='db_sqlite_driver',
    help='The driver to use for memoflow.app.diary_log',
)
CONF_OPTS.extend([driver, DIARY_DB_DRIVER])

GROUP_NAME = __name__.split('.')[-1]
ALL_OPTS = CONF_OPTS


def register_opts(conf):
    conf.register_opts(CONF_OPTS, group=GROUP_NAME)


def list_opts():
    return {GROUP_NAME: ALL_OPTS}