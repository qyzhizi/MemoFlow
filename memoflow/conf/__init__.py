from oslo_config import cfg


CONF = cfg.CONF

from memoflow.conf import diary_log
from memoflow.conf import server
from memoflow.conf import diary_log_second
from memoflow.conf import api

diary_log.register_opts(CONF)
server.register_opts(CONF)
diary_log_second.register_opts(CONF)
api.register_opts(CONF)