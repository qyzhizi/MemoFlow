from oslo_config import cfg
from dotenv import load_dotenv
load_dotenv()
import os

BASE_URL = 'https://dav.jianguoyun.com/dav/'
lzp_jianguoyun_count = os.getenv("LZP_JIANGUOYUN_COUNT")
lzp_jianguoyun_token = os.getenv("LZP_JIANGUOYUN_TOKEN")
lzp_jianguoyun_to_path = os.getenv("LZP_JIANGUOYUN_TO_PATH")

lrx_jianguoyun_count = os.getenv("LRX_JIANGUOYUN_COUNT")
lrx_jianguoyun_token = os.getenv("LRX_JIANGUOYUN_TOKEN")
lrx_jianguoyun_to_path = os.getenv("LRX_JIANGUOYUN_TO_PATH")

# 声明配置项
CONF_OPTS = [
    cfg.StrOpt('base_url',
               default=BASE_URL,
               help='坚果云的基地址'),
    cfg.StrOpt('lzp_jianguoyun_count',
                default=lzp_jianguoyun_count,
                help='lzp 的坚果云账号'),
    cfg.StrOpt('lzp_jianguoyun_token',
               default=lzp_jianguoyun_token,
               help='lzp 的坚果云token'),
    cfg.StrOpt('lzp_jianguoyun_to_path',
               default=lzp_jianguoyun_to_path,
               help='lzp 的坚果云笔记更新文件的路径'),

    cfg.StrOpt('lrx_jianguoyun_count',
                default=lrx_jianguoyun_count,
                help='lrx 的坚果云账号'),
    cfg.StrOpt('lrx_jianguoyun_token',
               default=lrx_jianguoyun_token,
               help='lrx 的坚果云token'),
    cfg.StrOpt('lrx_jianguoyun_to_path',
               default=lrx_jianguoyun_to_path,
               help='lrx 的坚果云笔记更新文件的路径'),

]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('api_conf')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)
