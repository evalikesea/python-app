import config_default

class Dict(dict):
    '''
    Simple dict but support acess as x.y style.
    '''
    def __init__(self, name=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        #zip() 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。
        #如果各个迭代器的元素个数不一致，则返回列表长度与最短的对象相同，利用 * 号操作符，可以将元组解压为列表。
        for k,v in zip(name, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s' % key")

    def __setattr__(self, key, value):
        self[key] = value

    def merge(defaults, override):
        r = {}
        for k, v in defaults.items():
            if k in override:
                if isinstance(v, dict):
                    r[k] = merge(v, override[k])
                else:
                    r[k] = override[k]
            else:
                r[k] = v
        return r

    def toDict(d):
        D = Dict()
        for k,v in d.items():
            D[k] = toDict(v) if isinstance(v, dict) else v
        return D

    configs = config_default.configs
    try:
        import config_override
        configs = merge(configs, config_override.configs)
    except ImportError:
        pass

    configs = toDict(configs)
