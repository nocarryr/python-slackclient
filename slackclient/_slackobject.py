
def iter_bases(obj, lastclass='object'):
    if type(lastclass) == type:
        lastclass = lastclass.__name__
    if type(obj) == type:
        cls = obj
    else:
        cls = obj.__class__
    while cls.__name__ != lastclass:
        yield cls
        cls = cls.__bases__[0]

class SlackObject(object):
    _parameters = []
    def __init__(self, **kwargs):
        self.server = kwargs.get('server')
        self.data = kwargs.get('data')
        parameters = self.parameters = set()
        for cls in iter_bases(self):
            if not hasattr(cls, '_parameters'):
                continue
            parameters |= set(cls._parameters)
        self.update(**kwargs)
        for param in parameters:
            if not hasattr(self, param):
                setattr(self, param, None)
    def update(self, **kwargs):
        parameters = self.parameters
        for key, val in kwargs.items():
            if key not in parameters:
                continue
            if getattr(self, key, None) == val:
                continue
            self.data[key] = val
            setattr(self, key, val)
    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return getattr(self, key, default)
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self, key):
            return getattr(self, key)
        return self.data[key]
    def keys(self):
        return self.data.keys()
    def values(self):
        return self.data.values()
    def items(self):
        return self.data.items()
        
class CreatorSlackObject(SlackObject):
    _parameters = ['creator']
    def __init__(self, **kwargs):
        self._creator = None
        super(CreatorSlackObject, self).__init__(**kwargs)
    @property
    def creator(self):
        return self._creator
    @creator.setter
    def creator(self, value):
        if isinstance(value, basestring):
            value = self.server.get_or_create_user(id=value)
        self._creator = value
