from oslo_config import cfg

# 声明配置项
CONF_OPTS = [     
    cfg.StrOpt('review_index_html_path',
               default='memoflow/data/client/diary_log/review.html',
               help='review html路径'),
    cfg.StrOpt('review_js_path',
                default="memoflow/data/client/diary_log/review.js",
                help='review js文件路径'),
    cfg.StrOpt('index_html_path',
               default='memoflow/data/client/diary_log/index.html',
               help='主页html路径'),
    cfg.StrOpt('index_css_path',
               default='memoflow/data/client/diary_log/index.css',
               help='主页css路径'),
    cfg.StrOpt('login_html_path',
               default='memoflow/data/client/diary_log/login/login.html',
               help='login.html路径'),
    cfg.StrOpt('log_js_path',
                default="memoflow/data/client/diary_log/log.js",
                help='主页的js文件路径'),
    # #clipboard数据库
    cfg.StrOpt('clipboard_html_path',
               default='memoflow/data/client/diary_log/clipboard/clipboard.html',
               help='clipboard html路径'),
    cfg.StrOpt('clipboard_js_path',
                default="memoflow/data/client/diary_log/clipboard/clipboard.js",
                help='clipboard js文件路径'),
    
    # vector_search
    cfg.StrOpt('vector_search_html_path',
                default='memoflow/data/client/diary_log/vector_search/vector_search.html',
                help='vector_search html路径'),
    cfg.StrOpt('vector_search_js_path',
                default="memoflow/data/client/diary_log/vector_search/vector_search.js",
                help='vector_search js文件路径'),


]

driver = cfg.StrOpt(
    'driver',
    default='driver',
    help='The driver to use for memoflow.app.diary_log',
)
CONF_OPTS.append(driver)

GROUP_NAME = __name__.split('.')[-1] + "_client"
ALL_OPTS = CONF_OPTS

def register_opts(conf):
    conf.register_opts(CONF_OPTS, group=GROUP_NAME)

def list_opts():
    return {GROUP_NAME: ALL_OPTS}