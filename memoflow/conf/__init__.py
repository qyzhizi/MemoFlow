from oslo_config import cfg


CONF = cfg.CONF

from memoflow.conf import server
from memoflow.conf import api
from memoflow.conf.app import diary_log
from memoflow.conf.app import diary_log_second
from memoflow.conf.driver import manager as driver_manager
from memoflow.conf import predict_image

from memoflow.conf.client import diary_log as diary_log_client

diary_log.register_opts(CONF)
server.register_opts(CONF)
diary_log_second.register_opts(CONF)
api.register_opts(CONF)
driver_manager.register_opts(CONF)
predict_image.register_opts(CONF)

diary_log_client.register_opts(CONF)
