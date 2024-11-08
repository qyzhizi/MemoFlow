# Copyright 2012 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2010 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Utility methods for working with WSGI servers."""

#import functools
#import itertools
#import re
import wsgiref.util
import logging as log
import routes.middleware
# from oslo_serialization import jsonutils
import json
import six
from six.moves import http_client
import webob.dec
import webob.exc
from memoflow.exception.visiable_exc import VisibleException
from memoflow.exception.visiable_exc import VisibleResponse
from memoflow.exception.visiable_exc import ServerErrorResponse

LOG = log.getLogger(__name__)

# Environment variable used to pass the request params
PARAMS_ENV = 'openstack.params'

JSON_ENCODE_CONTENT_TYPES = set(['application/json','application/json-home'])


class Router(object):
    """WSGI middleware that maps incoming requests to WSGI apps."""

    def __init__(self, mapper):
        """Create a router for the given routes.Mapper.
        Each route in `mapper` must specify a 'controller', which is a
        WSGI app to call.  You'll probably want to specify an 'action' as
        well and have your controller be an object that can route
        the request to the action-specific method.
        Examples:
          mapper = routes.Mapper()
          sc = ServerController()
          # Explicit mapping of one route to a controller+action
          mapper.connect(None, '/svrlist', controller=sc, action='list')
          # Actions are all implicitly defined
          mapper.resource('server', 'servers', controller=sc)
          # Pointing to an arbitrary WSGI app.  You can specify the
          # {path_info:.*} parameter so the target app can be handed just that
          # section of the URL.
          mapper.connect(None, '/v1.0/{path_info:.*}', controller=BlogApp())
        """
        self.map = mapper
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.map)

    #@webob.dec.wsgify(RequestClass=request_mod.Request)
    @webob.dec.wsgify()
    def __call__(self, req):
        """Route the incoming request to a controller based on self.map.
        If no match, return a 404.
        """
        return self._router

    @staticmethod
    #@webob.dec.wsgify(RequestClass=request_mod.Request)
    @webob.dec.wsgify()
    def _dispatch(req):
        """Dispatch the request to the appropriate controller.
        Called by self._router after matching the incoming request to a route
        and putting the information into req.environ.  Either returns 404
        or the routed WSGI app's response.
        """
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            msg = ('(%(url)s): The resource could not be found.' %
                   {'url': req.url})
            return webob.exc.HTTPNotFound()
#            return render_exception(exception.NotFound(msg),
#                                    request=req,
#                                    user_locale=best_match_language(req))
        app = match['controller']
        return app


class ComposingRouter(Router):
    def __init__(self, mapper=None, routers=None):
        if mapper is None:
            mapper = routes.Mapper()
        if routers is None:
            routers = []
        for router in routers:
            router.add_routes(mapper)
        super(ComposingRouter, self).__init__(mapper)


class ComposableRouter(Router):
    """Router that supports use by ComposingRouter."""""
    def __init__(self, mapper=None):
        if mapper is None:
            mapper = routes.Mapper()
        self.add_routes(mapper)
        super(ComposableRouter, self).__init__(mapper)

    def add_routes(self, mapper):
        """Add routes to given mapper."""""
        pass


# class SmarterEncoder(jsonutils.json.JSONEncoder):
#     """Help for JSON encoding dict-like objects."""

#     def default(self, obj):
#         if not isinstance(obj, dict) and hasattr(obj, 'iteritems'):
#             return dict(obj.iteritems())
#         return super(SmarterEncoder, self).default(obj)

class SmarterEncoder(json.JSONEncoder):
    """Help for JSON encoding dict-like objects."""

    def default(self, obj):
        if not isinstance(obj, dict) and hasattr(obj, 'items'):
            return dict(obj.items())
        return super().default(obj)

def render_response(body=None, status=None, headers=None, method=None):
    """Form a WSGI response."""
    if headers is None:
        headers = []
    else:
        headers = list(headers)
    headers.append(('Vary', 'X-Auth-Token'))

    if body is None:
        body = b''
        status = status or (http_client.NO_CONTENT,
                            http_client.responses[http_client.NO_CONTENT])
    else:
        content_types = [v for h, v in headers if h == 'Content-Type']
        if content_types:
            content_type = content_types[0]
        else:
            content_type = None

        if content_type is None or content_type in JSON_ENCODE_CONTENT_TYPES:
            # body = jsonutils.dump_as_bytes(body, cls=SmarterEncoder)
            body = json.dumps(body, indent=4, default=SmarterEncoder().default)
            if content_type is None:
                headers.append(('Content-Type', 'application/json'))
        status = status or (http_client.OK,
                            http_client.responses[http_client.OK])

    # NOTE(davechen): `mod_wsgi` follows the standards from pep-3333 and
    # requires the value in response header to be binary type(str) on python2,
    # unicode based string(str) on python3, or else keystone will not work
    # under apache with `mod_wsgi`.
    # keystone needs to check the data type of each header and convert the
    # type if needed.
    # see bug:
    # https://bugs.launchpad.net/keystone/+bug/1528981
    # see pep-3333:
    # https://www.python.org/dev/peps/pep-3333/#a-note-on-string-types
    # see source from mod_wsgi:
    # https://github.com/GrahamDumpleton/mod_wsgi(methods:
    # wsgi_convert_headers_to_bytes(...), wsgi_convert_string_to_bytes(...)
    # and wsgi_validate_header_value(...)).
    def _convert_to_str(headers):
        str_headers = []
        for header in headers:
            str_header = []
            for value in header:
                if not isinstance(value, str):
                    str_header.append(str(value))
                else:
                    str_header.append(value)
            # convert the list to the immutable tuple to build the headers.
            # header's key/value will be guaranteed to be str type.
            str_headers.append(tuple(str_header))
        return str_headers

    headers = _convert_to_str(headers)

    resp = webob.Response(body=body,
                          status='%d %s' % status,
                          headerlist=headers,
                          charset='utf-8')

    if method and method.upper() == 'HEAD':
        # NOTE(morganfainberg): HEAD requests should return the same status
        # as a GET request and same headers (including content-type and
        # content-length). The webob.Response object automatically changes
        # content-length (and other headers) if the body is set to b''. Capture
        # all headers and reset them on the response object after clearing the
        # body. The body can only be set to a binary-type (not TextType or
        # NoneType), so b'' is used here and should be compatible with
        # both py2x and py3x.
        stored_headers = resp.headers.copy()
        resp.body = b''
        for header, value in stored_headers.items():
            resp.headers[header] = value

    return resp


class BaseApplication(object):
    """Base WSGI application wrapper. Subclasses need to implement __call__."""

    @classmethod
    def factory(cls, global_config, **local_config):
        """Used for paste app factories in paste.deploy config files.
        Any local configuration (that is, values under the [app:APPNAME]
        section of the paste config) will be passed into the `__init__` method
        as kwargs.
        A hypothetical configuration would look like:
            [app:wadl]
            latest_version = 1.3
            paste.app_factory = keystone.fancy_api:Wadl.factory
        which would result in a call to the `Wadl` class as
            import keystone.fancy_api
            keystone.fancy_api.Wadl(latest_version='1.3')
        You could of course re-implement the `factory` method in subclasses,
        but using the kwarg passing it shouldn't be necessary.
        """
        return cls(**local_config)

    def __call__(self, environ, start_response):
        r"""Provide subclasses on how to implement __call__.
        Probably like this:
        @webob.dec.wsgify()
        def __call__(self, req):
          # Any of the following objects work as responses:
          # Option 1: simple string
          res = 'message\n'
          # Option 2: a nicely formatted HTTP exception page
          res = exc.HTTPForbidden(explanation='Nice try')
          # Option 3: a webob Response object (in case you need to play with
          # headers, or you want to be treated like an iterable, or or or)
          res = Response();
          res.app_iter = open('somefile')
          # Option 4: any wsgi app to be run next
          res = self.application
          # Option 5: you can get a Response object for a wsgi app, too, to
          # play with headers etc
          res = req.get_response(self.application)
          # You can then just return your response...
          return res
          # ... or set req.response and return None.
          req.response = res
        See the end of http://pythonpaste.org/webob/modules/dec.html
        for more info.
        """
        raise NotImplementedError('You must implement __call__')

class Application(BaseApplication):

    #@webob.dec.wsgify(RequestClass=request_mod.Request)
    @webob.dec.wsgify()
    def __call__(self, req):
        arg_dict = req.environ['wsgiorg.routing_args'][1]
        action = arg_dict.pop('action')
        del arg_dict['controller']

        params = req.environ.get(PARAMS_ENV, {})
        params.update(arg_dict)

        # TODO(termie): do some basic normalization on methods
        method = getattr(self, action)

        # NOTE(morganfainberg): use the request method to normalize the
        # response code between GET and HEAD requests. The HTTP status should
        # be the same.
        LOG.info('%(req_method)s %(uri)s', {
            'req_method': req.method.upper(),
            'uri': wsgiref.util.request_uri(req.environ),
        })

        params = self._normalize_dict(params)

        try:
            result = method(req, **params)
        except VisibleException as e:
            return VisibleResponse(str(e), status=e.status)
        except Exception as e:
            LOG.exception(f"error: {str(e)}")
            return ServerErrorResponse(
                "Server error. Please try again later or \
                contact the website developer", status=500)

        if result is None:
            return render_response(
                status=(http_client.NO_CONTENT,
                        http_client.responses[http_client.NO_CONTENT]))
        elif isinstance(result, six.string_types):
            return result
        elif isinstance(result, webob.Response):
            return result
        elif isinstance(result, webob.exc.WSGIHTTPException):
            return result
        # 添加的部分来检查result是否为字典
        elif isinstance(result, dict):  # 检查result是否为字典类型
            # 将字典转换为JSON字符串
            json_body = json.dumps(result)
            # 创建一个webob.Response对象，将内容类型设置为application/json
            response = webob.Response(body=json_body, content_type='application/json', charset='UTF-8')
            return response


    def _normalize_arg(self, arg):
        return arg.replace(':', '_').replace('-', '_')

    def _normalize_dict(self, d):
        return {self._normalize_arg(k): v for (k, v) in d.items()}
        
