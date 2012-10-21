from tornado.websocket import WebSocketHandler as BaseWebSocket
from tori.handler      import Handler

class WebSocket(BaseWebSocket, Handler):
    def __init__(self, *args, **kwargs):
        BaseWebSocket.__init__(self, *args, **kwargs)
        Handler.__init__(self)