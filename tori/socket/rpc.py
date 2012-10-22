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
    def __init__(self, method, id=None, data=None, service=None):
        self.id      = id or time.time()
        self.data    = data or None
        self.method  = method
        self.service = service or None

    def call(self):
        remote_call = self.service.__getattribute__(self.method)

        return remote_call(**self.data) if self.data else remote_call

class Response(object):
    def __init__(self, result, id):
        self.id     = id
        self.result = result

class Interface(WebSocket):
    def on_message(self, message):
        '''
        :type message: str or unicode

        The parameter ``message`` is supposed to be in JSON format:

        .. code-block:: javascript

            {
                "id":      unique_id,
                "service": service_name,
                "data":    parameter_object,
                "method":  method_name
            }

        '''

        remote = Remote(**(json.loads(message)))

        if not remote.service:
            remote.service = self

        response = Response(remote.call(), remote.id)

        self.write_message(
            json.dumps(ArrayConverter.instance().convert(response))
        )