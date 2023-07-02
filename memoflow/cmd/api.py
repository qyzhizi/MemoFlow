import logging
from memoflow.core.ConfigParse import ConfigParse
from memoflow.core import log_util
from memoflow.conf import CONF
from paste import deploy
from memoflow.core.wsgi_server import Server
from memoflow.core import dependency
from memoflow.core import backends
from memoflow.db import init_db

cp = ConfigParse(CONF.server['server_conf_path'])
cf_defaults = cp.read_file().get("default")
log_util.server_setup(cf_defaults.get("log_file"),'memoflow')

LOG = logging.getLogger(__name__)


def main():
    LOG.info("******************start**************************")

    # 初始化app使用的数据库
    LOG.info("初始化app使用的数据库")
    init_db()

    try:
        drivers = backends.load_backends()
        drivers.update(dependency.resolve_future_dependencies())
        LOG.info("cf_defaults:%s", cf_defaults)
        api_paste = cf_defaults.get("api_paste_path")
        app = deploy.loadapp("config:%s" % api_paste, relative_to="./")

        LOG.info("app: %s", app)
        server = Server(cf_defaults)
        server.start(app)
        server.wait()
    except Exception as e:
        LOG.info("caught an exception :%s" % (str(e)))
        raise e
