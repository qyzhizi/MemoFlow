import os
from oslo_config import cfg
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

FLOMO_API_URL = env_vars.get("FLOMO_API_URL", None)

DATABASE_ID = env_vars.get("DATABASE_ID", None)
NOTION_API_KEY = env_vars.get("NOTION_API_KEY", None)

GITHUB_TOKEN = env_vars.get("GITHUB_TOKEN", None)
GITHUB_REPO = env_vars.get("GITHUB_REPO", None)

GITHUB_CURRENT_SYNC_FILE_PATH = env_vars.get("GITHUB_CURRENT_SYNC_FILE_PATH", None)
GITHUB_SYNC_FILE_LIST = env_vars.get("GITHUB_SYNC_FILE_LIST", None)

SYNC_DATA_BASE_PATH= env_vars.get("SYNC_DATA_BASE_PATH", None)
SYNC_TABLE_NAME = env_vars.get("SYNC_TABLE_NAME", None)
REVIEW_TABLE_NAME = env_vars.get("REVIEW_TABLE_NAME", None)

DATA_BASE_CLIPBOARD_PATH = env_vars.get("DATA_BASE_CLIPBOARD_PATH", None)
CLIPBOARD_TABLE_NAME = env_vars.get("CLIPBOARD_TABLE_NAME", None)


#获取发送任务标志位
SEND_TO_GITHUB = bool(int(env_vars.get("SEND_TO_GITHUB", None)))
SEND_TO_JIANGUOYUN = bool(int(env_vars.get("SEND_TO_JIANGUOYUN", None)))


# 默认配置项
if GITHUB_CURRENT_SYNC_FILE_PATH == None:
    # github repo根目录下的memoflow_sync文件夹
    GITHUB_CURRENT_SYNC_FILE_PATH = "memoflow_sync/first_file.md"
if GITHUB_SYNC_FILE_LIST == None:
    GITHUB_SYNC_FILE_LIST = "memoflow_sync/first_file.md"   

if SYNC_DATA_BASE_PATH == None:
    # 当前工作目录下，db_data文件夹
    SYNC_DATA_BASE_PATH = os.path.join("db_data", "memoflow_sync_data.db")
if SYNC_TABLE_NAME == None:
    # get GITHUB_CURRENT_SYNC_FILE_PATH file name
    file_name = os.path.basename(GITHUB_CURRENT_SYNC_FILE_PATH)
    if file_name == "":
        file_name = "sync_data"
    file_name = file_name.split(".")[0] 
    # 当前工作目录下，db_data文件夹
    SYNC_TABLE_NAME = file_name 

if REVIEW_TABLE_NAME == None:
    REVIEW_TABLE_NAME = "review_diary_log"

if DATA_BASE_CLIPBOARD_PATH == None:
    # 当前工作目录下，db_data文件夹
    DATA_BASE_CLIPBOARD_PATH = os.path.join("db_data",
                                            "clipboard_data.db")
if CLIPBOARD_TABLE_NAME == None:
    CLIPBOARD_TABLE_NAME = "clipboard_log"


# 声明配置项
CONF_OPTS = [     
    cfg.StrOpt('SYNC_DATA_BASE_PATH',
               default=SYNC_DATA_BASE_PATH,
               help='同步数据库的路径'),
    cfg.StrOpt('SYNC_TABLE_NAME',
               default=SYNC_TABLE_NAME,
               help='同步数据库的表名'),
    cfg.StrOpt('REVIEW_TABLE_NAME',
               default=REVIEW_TABLE_NAME,
               help='review表'),
    cfg.StrOpt('REVIEW_TAGS',
               default='que,web',
               help='review 筛选标签'),
    cfg.StrOpt('FLOMO_API_URL',
            default=FLOMO_API_URL,
            help='flomo api url'),
    cfg.StrOpt('DATABASE_ID',
                default=DATABASE_ID,
                help='notion db id'),
    cfg.StrOpt('NOTION_API_KEY',
                default=NOTION_API_KEY,
                help='notion api key'),
    cfg.StrOpt('GITHUB_TOKEN',
               default=GITHUB_TOKEN,
               help='github access token'),
    cfg.StrOpt("GITHUB_REPO",
               default=GITHUB_REPO,
               help='github repo'),
    cfg.StrOpt("GITHUB_CURRENT_SYNC_FILE_PATH",
               default=GITHUB_CURRENT_SYNC_FILE_PATH,
               help='GITHUB_CURRENT_SYNC_FILE_PATH'),
    cfg.StrOpt("GITHUB_SYNC_FILE_LIST",
                default=GITHUB_SYNC_FILE_LIST,
                help='GITHUB_SYNC_FILE_LIST'),
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

]

driver = cfg.StrOpt(
    'driver',
    default='driver',
    help='The driver to use for memoflow.app.diary_log',
)
CONF_OPTS.append(driver)

GROUP_NAME = __name__.split('.')[-1]
ALL_OPTS = CONF_OPTS

def register_opts(conf):
    conf.register_opts(CONF_OPTS, group=GROUP_NAME)

def list_opts():
    return {GROUP_NAME: ALL_OPTS}