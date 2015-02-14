from _slackobject import SlackObject

class User(SlackObject):
    _parameters = [
        'id', 
        'name', 
        'deleted', 
        'color', 
        'is_admin', 
        'is_owner', 
        'is_primary_owner', 
        'is_restricted', 
        'is_ultra_restricted', 
        'has_files', 
    ]
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        pkwargs = kwargs.get('profile', {})
        pkwargs['server'] = self.server
        pkwargs['data'] = self.data.get('profile', {})
        self.profile = Profile(**pkwargs)
    def update(self, **kwargs):
        super(User, self).update(**kwargs)
        if not hasattr(self, 'profile'):
            return
        self.profile.update(**kwargs.get('profile', {}))
    def __repr__(self):
        return str(self)
    def __str__(self):
        if self.name is not None:
            return self.name
        return self.id

class Profile(SlackObject):
    _parameters = [
        'first_name', 
        'last_name', 
        'email', 
    ]
    
