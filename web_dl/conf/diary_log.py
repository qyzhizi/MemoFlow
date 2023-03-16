from oslo_config import cfg

# 声明配置项
CONF_OPTS = [     
    cfg.StrOpt('data_base_path',
               default='/root/git_rep/dl/web_dl/data/diary_log/diary_log.db',
               help='sqlite3数据库的路径'),
    cfg.StrOpt('index_html_path',
               default='/root/git_rep/dl/web_dl/data/diary_log/index.html',
               help='主页html路径'),
    cfg.StrOpt('log_js_path',
                default="/root/git_rep/dl/web_dl/data/diary_log/log.js",
                help='主页的js文件路径'),
    cfg.StrOpt('flomo_api_url',
            #@todo os.environ
            default="https://flomoapp.com/iwh/MzA4ODk/bf5338002eb49cbd323c672e03eb5b1b/",
            help='flomo api url')
]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('diary_log')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)