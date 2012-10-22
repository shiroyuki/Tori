'''
Generic Web Socket Module
=========================

:Author: Juti Noppornpitak
:Status: Stable
:Last Update: |today|
'''

from tornado.websocket import WebSocketHandler as BaseWebSocket

from tori.handler import Handler

class WebSocket(BaseWebSocket, Handler):
    '''
    Session-enabled Web Socket Handler
    '''
    _channel_table = {}

    def __init__(self, *args, **kwargs):
        BaseWebSocket.__init__(self, *args, **kwargs)
        Handler.__init__(self)

        self._channel_table[self.__hash__()] = self

    def broadcast(self, message, scopes=[]):
        current_session_id = self.session.id

        for object_hash in self._channel_table:
            channel = self._channel_table[object_hash]

            if current_session_id == channel.session.id:
                continue

            channel.write_message(message)

    def close(self):
        pass

    def on_close(self):
        del self._channel_table[self.__hash__()]

        self.close()