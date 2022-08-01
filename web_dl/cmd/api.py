
from paste import deploy
import logging

from web_dl.ConfigParse import ConfigParse
from web_dl import log_util
from web_dl.wsgi import Server
from web_dl.common import dependency
from web_dl.common import backends

LOG = logging.getLogger(__name__)
cp = ConfigParse("/root/git_rep/dl/web_dl/etc/web_dl/web-dl.conf")
cf_defaults = cp.read_file().get("default")

log_util.setup(level=logging.INFO,
               outs=[log_util.RotatingFile(filename=cf_defaults.get("log_file"),
                                           level=logging.INFO,
                                           max_size_bytes=1000000,
                                           backup_count=10)],
               program_name="web_dl",
               capture_warnings=True)


def main():
    LOG.info("******************start**************************")
    try:
        drivers = backends.load_backends()
        drivers.update(dependency.resolve_future_dependencies())
        LOG.info("cf_defaults:%s", cf_defaults)
        api_paste = cf_defaults.get("api_paste_path")
        app = deploy.loadapp("config:%s" % api_paste)

        LOG.info("app: %s", app)
        server = Server(cf_defaults)
        server.start(app)
        server.wait()
    except Exception as e:
        LOG.info("caught an exception :%s" % (str(e)))
        raise e
