from _slackobject import CreatorSlackObject
from _channel import ChannelBase

class Group(ChannelBase):
    def __init__(self, **kwargs):
        super(Group, self).__init__(**kwargs)
        tkwargs = kwargs.get('topic', {})
        tkwargs['server'] = self.server
        tkwargs['data'] = self.data.get('topic', {})
        self.topic = Topic(**tkwargs)
        pkwargs = kwargs.get('purpose', {})
        pkwargs['server'] = self.server
        pkwargs['data'] = self.data.get('purpose', {})
        self.purpose = Purpose(**pkwargs)
    def update(self, **kwargs):
        super(Group, self).update(**kwargs)
        if not hasattr(self, 'topic'):
            return
        self.topic.update(**kwargs.get('topic', {}))
        self.purpose.update(**kwargs.get('purpose', {}))
    def get_history(self, **kwargs):
        kwargs['channel'] = self.id
        return self._get_history('groups.history', **kwargs)
        
class TopicBase(CreatorSlackObject):
    _parameters = [
        'value', 
        'last_set', 
    ]
    def __str__(self):
        return self.value
    
class Topic(TopicBase):
    pass
    
class Purpose(TopicBase):
    pass
