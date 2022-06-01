from .middleware import Middleware
from web_dl.controller.version import VersionController
import re
import logging

LOG = logging.getLogger(__name__)


class VersionFilter(Middleware):

    def __init__(self, app):
        self.application = app
        self.version = VersionController()
        self.version_uri_regex = re.compile(r"^v(\d+)\.?(\d+)?")
        super(VersionFilter, self).__init__(app)

    def process_request(self, req):
        #import pdb; pdb.set_trace()
        msg = ("Processing request: %(method)s %(path)s Accept: "
               "%(accept)s" % {'method': req.method,
                               'path': req.path, 'accept': req.accept})
        LOG.info(msg)

        if req.path_info_peek() in ("version", ""):
            LOG.info("req.path_info_peek()")
            LOG.info(req.path_info_peek())
            return self.version
        match = self.match_version_string(req.path_info_peek(), req)
        if match:
            LOG.info("matched")
            major_version = req.environ['api.major_version']
            minor_version = req.environ['api.minor_version']
            if (major_version == 1 and minor_version == 0):
                LOG.info("Matched versioned URI. "
                         "Version: %(major_version)d.%(minor_version)d"
                         % {'major_version': major_version,
                            'minor_version': minor_version})
                # Strip the version from the path
                req.path_info_pop()
                return None
            else:
                LOG.debug("Unknown version in versioned URI: "
                          "%(major_version)d.%(minor_version)d. "
                          "Returning version choices."
                          % {'major_version': major_version,
                             'minor_version': minor_version})
                return self.version
        else:
            LOG.info("the version is not allow")
            return self.version

    def match_version_string(self, subject, req):
        match = self.version_uri_regex.match(subject)
        if match:
            major_version, minor_version = match.groups(0)
            LOG.info("major_version, minor_version:" 
                "%(major_version)s.%(minor_version)s"
                %{'major_version': major_version,
                            'minor_version': minor_version})
            major_version = int(major_version)
            minor_version = int(minor_version)
            req.environ['api.major_version'] = major_version
            req.environ['api.minor_version'] = minor_version
        return match is not None


def version_filter(local_conf, **global_conf):
    def filter(app):
        import pdb; pdb.set_trace()
        return VersionFilter(app)

    return filter
