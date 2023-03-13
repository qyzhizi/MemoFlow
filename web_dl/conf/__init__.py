from oslo_config import cfg


CONF = cfg.CONF

from web_dl.conf import diary_log
from web_dl.conf import server
from web_dl.conf import diary_log_lrx

diary_log.register_opts(CONF)
server.register_opts(CONF)
diary_log_lrx.register_opts(CONF)