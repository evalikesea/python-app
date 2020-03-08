import asyncio, os, inspect, logging,functools
from urllib import parse
from aiohttp import web
from apis import APIError

def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

def get_required_kw_args(fn):
    #inspect.signature（fn)将返回一个inspect.Signature类型的对象，值为fn这个函数的所有参数
    #inspect.Signature对象的paramerters属性是一个mappingproxy（映射）类型的对象，值为一个有序字典（Orderdict)。
    #这个字典里的key是即为参数名，str类型
    #这个字典里的value是一个inspect.Parameter类型的对象，根据我的理解，这个对象里包含的一个参数的各种信息
    #inspect.Parameter对象的kind属性是一个_ParameterKind枚举类型的对象，值为这个参数的类型（可变参数，关键词参数，etc）
    #inspect.Parameter对象的default属性：如果这个参数有默认值，即返回这个默认值，如果没有，返回一个inspect._empty类。
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)
def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        #KEYWORD_ONLY 值必须作为关键字参数提供。 KEYWORD_ONLY 参数是在Python函数定义中的*或* args条目之后出现的参数。
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        #VAR_KEYWORD参数是在Python函数定义中的与**kw 对等的参数。
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found =True
            continue
        #VAR_POSITIONAL参数是在Python函数定义中的与*args对等的tuple位置参数。
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found

#从URL函数中分析其需要接收的参数，从request中获取必要的参数，调用URL函数，然后把结果转换为web.Response对象
class RequestHandler(object):
    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_args(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupport Content-Type: %s' % request.content_type)

            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._has_named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._has_named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k,v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)

def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

def add_route(app,fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))

def add_routes(app, module_name):
    #rfind返回字符串最后一次出现的位置，如果没有匹配项则返回-1。
    #str.rfind(str, beg=0 end=len(string))
    n = module_name.rfind('.')
    if n == (-1):
        #__import__ 函数用于动态加载类和函数,返回元组列表。语法：__import__(name[, globals[, locals[, fromlist[, level]]]])
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        #返回一个对象属性值。语法：getattr(object, name[, default])，default -- 默认返回值，如果不提供该参数，在没有对应属性时，将触发 AttributeError
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        #continue 语句是一个删除的效果，他的存在是为了删除满足循环条件下的某些不需要的成分
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__',None)
            path = getattr(fn, '__route__',None)
            if method and path:
                add_route(app, fn)

