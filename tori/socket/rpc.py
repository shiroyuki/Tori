'''
Remote Procedure Call Module
============================

:Author: Juti Noppornpitak
:Status: Stable/Testing
:Last Update: |today|
'''

import json
import time

from tori.data.converter   import ArrayConverter
from tori.socket.websocket import WebSocket

class Remote(object):
    def __init__(self, command, id=None, data=None, service=None):
        self.id      = id or time.time()
        self.command = command
        self.data    = data or None
        self.service = service or None

    def call(self):
        remote_call = self.service.__getattr__(self.command)

        return remote_call(**data) if self.data else remote_call

class Response(object):
    def __init__(self, result, id):
        self.id     = id
        self.result = result

class RemoteInterface(WebSocket):
    def on_message(self, message):
        remote = RemoteCall(**(json.loads(message)))

        if not remote.service:
            remote.service = self

        response = Response(remote.call(), remote.id)

        self.write_message(
            json.dumps(ArrayConverter.instance().convert(response))
        )