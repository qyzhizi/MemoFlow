from oslo_config import cfg
from dotenv import load_dotenv
load_dotenv()
import os

BASE_URL = 'https://dav.jianguoyun.com/dav/'
JIANGUOYUN_COUNT = os.getenv("JIANGUOYUN_COUNT")
JIANGUOYUN_TOKEN = os.getenv("JIANGUOYUN_TOKEN")
JIANGUOYUN_TO_PATH = os.getenv("JIANGUOYUN_TO_PATH")

second_jianguoyun_count = os.getenv("second_JIANGUOYUN_COUNT")
second_jianguoyun_token = os.getenv("second_JIANGUOYUN_TOKEN")
second_jianguoyun_to_path = os.getenv("second_JIANGUOYUN_TO_PATH")

# 声明配置项
CONF_OPTS = [
    cfg.StrOpt('base_url',
               default=BASE_URL,
               help='坚果云的基地址'),
    cfg.StrOpt('JIANGUOYUN_COUNT',
                default=JIANGUOYUN_COUNT,
                help='坚果云账号'),
    cfg.StrOpt('JIANGUOYUN_TOKEN',
               default=JIANGUOYUN_TOKEN,
               help='坚果云token'),
    cfg.StrOpt('JIANGUOYUN_TO_PATH',
               default=JIANGUOYUN_TO_PATH,
               help='坚果云笔记更新文件的路径'),

    cfg.StrOpt('second_jianguoyun_count',
                default=second_jianguoyun_count,
                help='second 的坚果云账号'),
    cfg.StrOpt('second_jianguoyun_token',
               default=second_jianguoyun_token,
               help='second 的坚果云token'),
    cfg.StrOpt('second_jianguoyun_to_path',
               default=second_jianguoyun_to_path,
               help='second 的坚果云笔记更新文件的路径'),
]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('api_conf')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)
