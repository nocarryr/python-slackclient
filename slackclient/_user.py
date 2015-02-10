
class User(object):
    _conf_attrs = ['name']
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
    def update(self, **kwargs):
        for attr in self._conf_attrs:
            val = kwargs.get(attr)
            if val is None:
                continue
            if getattr(self, attr, None) == val:
                continue
            setattr(self, attr, val)
    def __repr__(self):
        return str(self)
    def __str__(self):
        if self.name is not None:
            return self.name
        return self.id
