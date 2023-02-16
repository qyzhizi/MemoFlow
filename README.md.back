## web_dl

### 安装
**clone 代码**
 ```
 git clone https://github.com/CaesarLinsa/web_dl.git
``` 
将etc/web_dl下api-paste 放置在linux环境/etc/web_dl 下，执行
```
python setup.py install
```
生成可执行文件`web_dl`，执行web_dl即可启动服务

### 简介

**web_dl** 是个轻量型的python web框架。

* 内核自带的webob和routes wsgi接口，实现请求分发调用。
* 使用eventlet 协程库，提高并发性能。

* PasteDeploy请求过滤和拦截处理

### 代码接口

代码中各个目录的含义，如下：

```
├── etc
│   └── web_dl
│       └── api-paste.ini     # PasteDeploy 配置文件
├── README.md
├── setup.cfg
├── setup.py
└── web_dl
    ├── cmd
    │   ├── api.py           # 服务启动入口main函数
    │   └── __init__.py
    ├── controller
    │   ├── __init__.py
    │   ├── v1
    │   │   ├── demo_controller.py    # controller层
    │   │   └── __init__.py
    │   └── version.py
    ├── handler.py        # 根据req中environ 调用controller中方法
    ├── __init__.py
    ├── log_util.py        # 日志类 
    |-- wsgi.py   # 使用eventlet多协程Server
    ├── middleware 
    │   ├── __init__.py
    │   ├── middleware.py   # 中间件基类， 定义请求前后处理
    │   └── versionfilter.py  # 一个过滤器例子，用于url中非v1返回版本，否则转发给app
    └── web_dl.py  # 定义请求路由分发
```

### 当用户请求一个url

根据paste-api.ini ，请求先通过versionfilter，再到apiv1app

```
[pipeline:web_dl]
pipeline = versionfilter apiv1app

[app:apiv1app]
paste.app_factory = web_dl.web_dl:Router

[filter:versionfilter]
paste.filter_factory = web_dl.middleware.versionfilter:version_filter
```

#### versionfilter

请求经过versionfilter拦截器，调用web_dl.middleware.versionfilter中version_filter

```python
def version_filter(local_conf, **global_conf):
    def filter(app):
        return VersionFilter(app)

    return filter
```

VersionFilter 继承Middleware类，实例化时，调用其`__call__`方法，基类不实现`process_request`， 调用过滤器中的process_request进行到达app前处理。

`__call__`方法：

```python
    @webob.dec.wsgify
    def __call__(self, req):
        """ 过滤器，process_request在controller前处理，process_response
         controller响应后处理。若process_request有响应返回，则返回，否则继续执行
        """
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.application)
        return self.process_response(response)
```

`process_request` ,VersionFilter 中对版本进行判断，返回为None时，进入下一阶段处理。

```python
    def process_request(self, req):
        msg = ("Processing request: %(method)s %(path)s Accept: "
               "%(accept)s" % {'method': req.method,
                               'path': req.path, 'accept': req.accept})
        LOG.info(msg)

        if req.path_info_peek() in ("version", ""):
            return self.version
        match = self.match_version_string(req.path_info_peek(), req)
        if match:
            ...
            else:
                ...
                return self.version
        else:
            LOG.info("the version is not allow")
            return self.version
```

#### apiv1app

请求路由规则如下， action为controller中的方法名，注意demo为实例化对象，否则在调用时出现`unbound method`错误。

```python
        demo = create_handler()
        connect(controller=demo,
                routes=[
                    {
                        'url': '/index/{name}',
                        'action': 'index',
                        'method': ["GET"]
                    }
```

经过dispatcher方法，从请求中读取返回实例化类对象

```python
    @staticmethod
    @wsgify
    def dispatcher(req):
        try:
            match = req.environ['wsgiorg.routing_args'][1]
            if not match:
                return webob.exc.HTTPNotFound()
            controller = match.pop('controller', None)
            return controller
        except Exception as e:
            raise e
```

实例化对象初始化时，调用其`__call__`方法，此方法在handler.py中，为每个controller在自己的controller 模块外注册的方法。

```python
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
```

`__call__` 获取请求中action和方法参数，从而调用controller中的方法。如demoController中注册Handler，如下：

```python
def create_handler():
    return Handler(DemoController())
```


