from _slackobject import CreatorSlackObject
from _message import Message

class TimestampError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
        
class ChannelBase(CreatorSlackObject):
    _parameters = [
        'id', 
        'name', 
        'created', 
        'is_archived', 
    ]
    def __init__(self, **kwargs):
        self.members = {}
        self.messages = {}
        super(ChannelBase, self).__init__(**kwargs)
        
    def update(self, **kwargs):
        super(ChannelBase, self).update(**kwargs)
        for member in kwargs.get('members', []):
            self.add_member(member)
            
    def add_member(self, member):
        if isinstance(member, basestring):
            member = self.server.get_or_create_user(id=member)
        self.members[member.id] = member
        
    def add_message(self, **kwargs):
        kwargs.setdefault('server', self.server)
        msg = Message(**kwargs)
        if msg.id in self.messages:
            other = self.messages[msg.id]
            if msg == other:
                return other
            raise TimestampError('Duplicate Message timestamps found:\n{0!r}, \n{1!r}'.format(msg, other))
        self.messages[msg.id] = msg
        return msg
        
    def _get_history(self, api_method, **kwargs):
        reply = self.server.api_call_parse(api_method, **kwargs)
        for msg in reply['messages']:
            last_message = self.add_message(**msg)
        return dict(last_ts=last_message.ts, has_more=reply.get('has_more'))
        
    def get_all_history(self, **kwargs):
        oldest = kwargs.get('oldest')
        latest = kwargs.get('latest')
        hkwargs = dict(count=1000)
        if latest is not None:
            hkwargs['latest'] = latest
        if oldest is not None:
            hkwargs['oldest'] = oldest
        while True:
            r = self.get_history(**hkwargs)
            if not r.get('has_more'):
                break
            hkwargs['oldest'] = r['last_ts']
        return self.messages
        
    def __eq__(self, compare_str):
        if self.name == compare_str or self.id == compare_str:
            return True
        else:
            return False

    def __str__(self):
        data = ""
        for key in self.__dict__.keys():
            data += "{} : {}\n".format(key, str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

class Channel(ChannelBase):
    _parameters = ['is_general', ]
    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)
    def get_history(self, **kwargs):
        kwargs['channel'] = self.id
        return self._get_history('channels.history', **kwargs)

