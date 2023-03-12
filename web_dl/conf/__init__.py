from oslo_config import cfg


CONF = cfg.CONF

from web_dl.conf import diary_log
from web_dl.conf import server

diary_log.register_opts(CONF)
server.register_opts(CONF)