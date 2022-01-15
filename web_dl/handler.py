import webob.dec


class Handler(object):

    def __init__(self, controller):
        self.controller = controller

    @webob.dec.wsgify
    def __call__(self, req):
        match = req.environ["wsgiorg.routing_args"][1]
        action = match.pop("action", None)
        method = getattr(self.controller, action)
        if match:
            return method(req, **match)
        return method(req)
