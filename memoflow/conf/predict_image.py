from oslo_config import cfg

# 声明配置项
CONF_OPTS = [     
    cfg.StrOpt('imagenet_id2class_filepath',
               default='data/predict_image/imagenet_class.txt',
               help='imagenet id to class txt file path'),
    cfg.BoolOpt("IMAGENET_PREDICT_USE_GPU",
               default=False,
               help='GPU inference is not used by default'),
    cfg.StrOpt('index_html_path',
               default='data/predict_image/index.html',
               help='predict_image index.html file path')           
]

def register_opts(conf):
    
    # 声明group
    opt_group = cfg.OptGroup('predict_image')
    # 注册group
    conf.register_group(opt_group)
    
    conf.register_opts(CONF_OPTS, group=opt_group)