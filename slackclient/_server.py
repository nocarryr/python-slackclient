from _config import config
from _slackrequest import SlackRequest
from _channel import Channel
from _group import Group
from _user import User
from _util import SearchList

from websocket import create_connection
import json

class Server(object):
    def __init__(self, token=None, connect=True):
        if token is None:
            token = config.TOKEN
        self.token = token
        self.username = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = {}
        self.channels = SearchList()
        self.groups = {}
        self.connected = False
        self.pingcounter = 0
        self.api_requester = SlackRequest()

        if connect:
            self.rtm_connect()
    def __eq__(self, compare_str):
        if compare_str == self.domain or compare_str == self.token:
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

    def rtm_connect(self):
        reply = self.api_requester.do(self.token, "rtm.start")
        if reply.code != 200:
            raise SlackConnectionError
        else:
            reply = json.loads(reply.read())
            if reply["ok"]:
                self.parse_slack_login_data(reply)
            else:
                raise SlackLoginError

    def parse_slack_login_data(self, login_data):
        self.login_data = login_data
        self.domain = self.login_data["team"]["domain"]
        self.username = self.login_data["self"]["name"]
        self.parse_channel_data(login_data["channels"])
        self.parse_channel_data(login_data["groups"])
        self.parse_channel_data(login_data["ims"])
        try:
            self.websocket = create_connection(self.login_data['url'])
            self.websocket.sock.setblocking(0)
        except:
            raise SlackConnectionError

    def parse_channel_data(self, channel_data):
        for channel in channel_data:
            if "name" not in channel:
                channel["name"] = channel["id"]
            if "members" not in channel:
                channel["members"] = []
            self.attach_channel(**channel)
        
    def get_all_channels(self):
        reply = self.api_call_parse('channels.list')
        self.parse_channel_data(reply['channels'])
        return self.channels
        
    def get_all_groups(self):
        reply = self.api_call_parse('groups.list')
        for group_data in reply['groups']:
            group_data['server'] = self
            group = Group(**group_data)
            self.groups[group.id] = group
        return self.groups
        
    def get_all_users(self):
        reply = self.api_call_parse('users.list')
        for user_data in reply['members']:
            self.get_or_create_user(**user_data)
        return self.users
        
    def get_or_create_user(self, **kwargs):
        uid = kwargs.get('id')
        user = self.users.get(uid)
        if user is None:
            user = User(**kwargs)
            self.users[uid] = user
        else:
            user.update(**kwargs)
        return user

    def send_to_websocket(self, data):
        """Send (data) directly to the websocket."""
        data = json.dumps(data)
        self.websocket.send(data)

    def ping(self):
        return self.send_to_websocket({"type": "ping"})

    def websocket_safe_read(self):
        """Returns data if available, otherwise ''. Newlines indicate multiple messages """
        data = ""
        while True:
            try:
                data += "{}\n".format(self.websocket.recv())
            except:
                return data.rstrip()

    def attach_channel(self, **kwargs):
        kwargs['server'] = self
        self.channels.append(Channel(**kwargs))

    def join_channel(self, name):
        print(self.api_requester.do(self.token, "channels.join?name={}".format(name)).read())

    def api_call_parse(self, method, **kwargs):
        reply = json.loads(self.api_call(method, **kwargs))
        if not reply.get('ok'):
            raise SlackLoginError
        return reply
        
    def api_call(self, method, **kwargs):
        reply = self.api_requester.do(self.token, method, kwargs)
        return reply.read()

class SlackConnectionError(Exception):
    pass

class SlackLoginError(Exception):
    pass
