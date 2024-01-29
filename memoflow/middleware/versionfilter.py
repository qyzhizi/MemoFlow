import logging
import json
import re
from six.moves import http_client
import webob.dec
import webob
from webob import Response

from .middleware import Middleware
#from memoflow.controller.version import VersionController

LOG = logging.getLogger(__name__)


class VersionController(object):

    @webob.dec.wsgify
    def __call__(self, req):
        if req.path_info_peek() in ("favicon.ico", ):
            try:
                # 打开文件并读取内容
                with open('favicon.ico', 'rb') as f:
                    favicon_data = f.read()
                # 创建 Response 对象并设置 MIME 类型
                response = Response(body=favicon_data, content_type='image/vnd.microsoft.icon')
                # 返回响应
                return response
            except Exception as e:
                # 如果发生异常，返回错误信息
                response = Response(body=str(e), content_type='text/plain', status=500)
                return response
        version_obj = {
            "version": "v1",
            "author": "qyzhizi",
            "url": self.get_href(req)
        }
        body_str = json.dumps(dict(version_obj))
        # application/json
        response = webob.response.Response(request=req,
                                           status=http_client.MULTIPLE_CHOICES,
                                           content_type="text/plain") #text/plain
        #response.body = body_str
        
        response.text = body_str  # python3
        return response

    def get_href(self, req):
        return "%s/v1/" % req.host_url


class VersionFilter(Middleware):

    def __init__(self, app):
        self.application = app
        self.version = VersionController()
        self.version_uri_regex = re.compile(r"^v(\d+)\.?(\d+)?")
        super(VersionFilter, self).__init__(app)

    def process_request(self, req):
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


#def version_filter(local_conf, **global_conf):
#    def filter(app):
#        return VersionFilter(app)
#
#    return filter

