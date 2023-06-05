from oslo_config import cfg


CONF = cfg.CONF

from memocard.conf import diary_log
from memocard.conf import server
from memocard.conf import diary_log_second
from memocard.conf import api

diary_log.register_opts(CONF)
server.register_opts(CONF)
diary_log_second.register_opts(CONF)
api.register_opts(CONF)