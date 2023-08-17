from oslo_config import cfg
from dotenv import dotenv_values, find_dotenv
env_vars = dotenv_values(find_dotenv())
# load_dotenv()
import os

BASE_URL = 'https://dav.jianguoyun.com/dav/'
JIANGUOYUN_COUNT = env_vars.get("JIANGUOYUN_COUNT",  None)
JIANGUOYUN_TOKEN = env_vars.get("JIANGUOYUN_TOKEN",  None)
JIANGUOYUN_TO_PATH = env_vars.get("JIANGUOYUN_TO_PATH",  None)

second_jianguoyun_count = env_vars.get("SECOND_JIANGUOYUN_COUNT",  None)
second_jianguoyun_token = env_vars.get("SECOND_JIANGUOYUN_TOKEN",  None)
second_jianguoyun_to_path = env_vars.get("SECOND_JIANGUOYUN_TO_PATH",  None)

AZURE_OPENAI_ENDPOINT = env_vars.get("AZURE_OPENAI_ENDPOINT",  None)
AZURE_OPENAI_KEY = env_vars.get("AZURE_OPENAI_KEY",  None)

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

    cfg.StrOpt('AZURE_OPENAI_ENDPOINT',
                default=AZURE_OPENAI_ENDPOINT,
                help='azure openai endpoint'),
    cfg.StrOpt('AZURE_OPENAI_KEY',
                default=AZURE_OPENAI_KEY,
                help='azure openai key'),
]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('api_conf')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)
