from _slackobject import SlackObject

class Message(SlackObject):
    _parameters = [
        'type',
        'user', 
        'ts', 
        'subtype', 
        'text', 
    ]
    def __init__(self, **kwargs):
        self._user = None
        super(Message, self).__init__(**kwargs)
    @property
    def id(self):
        return self.ts
    @property
    def user(self):
        return self._user
    @user.setter
    def user(self, value):
        if isinstance(value, basestring):
            value = self.server.get_or_create_user(id=value)
        self._user = value
    def __eq__(self, other):
        for param in self.parameters:
            if getattr(self, param) != getattr(other, param, None):
                return False
        return True
    def __repr__(self):
        params = list(self.parameters)
        return str(dict(zip(params, [getattr(self, p) for p in params])))
    def __str__(self):
        return self.text
