from oslo_config import cfg

# 声明配置项
CONF_OPTS = [     
    cfg.StrOpt('SYNC_DATA_BASE_PATH',
               default='db_data/diary_log_second/diary_log_second.db',
               help='sqlite3数据库的路径'),
    cfg.StrOpt('SYNC_TABLE_NAME',
                default='diary_log_second',
                help='sqlite3数据库的表名'),
    cfg.StrOpt('index_html_path',
               default='memoflow/data/app/diary_log_second/index.html',
               help='主页html路径'),
    cfg.StrOpt('log_js_path',
                default="memoflow/data/app/diary_log_second/log.js",
                help='主页的js文件路径'),
]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('diary_log_second')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)
    