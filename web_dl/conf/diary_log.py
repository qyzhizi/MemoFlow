from oslo_config import cfg
from dotenv import load_dotenv
load_dotenv()
import os

flomo_api_url = os.getenv("FLOMO_API_URL")
database_id = os.getenv("DATABASE_ID")
notion_api_key = os.getenv("NOTION_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
github_repo = os.getenv("GITHUB_REPO")
github_file_path = os.getenv("GITHUB_FILE_PATH")


# 声明配置项
CONF_OPTS = [     
    cfg.StrOpt('data_base_path',
               default='data/diary_log/diary_log.db',
               help='sqlite3数据库的路径'),
    cfg.StrOpt('diary_log_table',
               default='diary_log',
               help='存储笔记的表'),
    cfg.StrOpt('review_diary_log_table',
               default='review_diary_log',
               help='存储笔记的表'),
    cfg.StrOpt('review_index_html_path',
               default='data/diary_log/review.html',
               help='review html路径'),
    cfg.StrOpt('review_js_path',
                default="data/diary_log/review.js",
                help='review js文件路径'),
    cfg.StrOpt('review_tags',
               default='que,web',
               help='存储笔记的表'),
    cfg.StrOpt('index_html_path',
               default='data/diary_log/index.html',
               help='主页html路径'),
    cfg.StrOpt('log_js_path',
                default="data/diary_log/log.js",
                help='主页的js文件路径'),
    cfg.StrOpt('flomo_api_url',
            #@todo os.environ
            default=flomo_api_url,
            help='flomo api url'),
    cfg.StrOpt('database_id',
                default=database_id,
                help='notion db id'),
    cfg.StrOpt('notion_api_key',
                default=notion_api_key,
                help='notion api key'),
    cfg.StrOpt('github_token',
               default=github_token,
               help='github access token'),
    cfg.StrOpt("github_repo",
               default=github_repo,
               help='github repo'),
    cfg.StrOpt("github_file_path",
               default=github_file_path,
               help='github_file_path'),
    # #clipboard数据库
    cfg.StrOpt('clipboard_html_path',
               default='data/diary_log/clipboard/clipboard.html',
               help='clipboard html路径'),
    cfg.StrOpt('clipboard_js_path',
                default="data/diary_log/clipboard/clipboard.js",
                help='clipboard js文件路径'),
    cfg.StrOpt("clipboard_data_base_path",
               default='data/diary_log/clipboard/clipboard_log.db',
               help='clipboard_log db file path'),
    cfg.StrOpt("clipboard_log_table",
               default='clipboard_log',
               help='clipboard_log table name')

]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('diary_log')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)