from oslo_config import cfg

# 声明配置项
SEVER_OPTS = [     
    cfg.StrOpt('server_conf_path',
               default='etc/memoflow/memoflow.conf',
               help='服务配置文件的路径'),
]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('server')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(SEVER_OPTS, group=opt_group)