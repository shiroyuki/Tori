"""
Generic Web Socket Module
=========================

:Author: Juti Noppornpitak
:Status: Stable
:Last Update: |today|
"""

from tornado.websocket import WebSocketHandler as BaseWebSocket

from tori.centre             import services
from tori.session.generator  import GuidGenerator
from tori.session.controller import Controller as SessionController

class WebSocket(BaseWebSocket):
    """ Web Socket Handler with extension to session controller """

    _guid_generator = GuidGenerator()
    _channel_table = {}

    def __init__(self, *args, **kwargs):
        BaseWebSocket.__init__(self, *args, **kwargs)

        self._session = None

        self._channel_table[self.__hash__()] = self

    def component(self, name, fork_component=False):
        """
        Get the (re-usable) component from the initialized Imagination
        component locator service.

        :param `name`:           the name of the registered re-usable component.
        :param `fork_component`: the flag to fork the component
        :return:                 module, package registered or ``None``
        """

        if not services.has(name):
            return None

        return services.fork(name)\
        if   fork_component\
        else services.get(name)

    @property
    def session(self):
        """ Session Controller

        :rtype: tori.session.controller.Controller
        """
        if not self.component('session'):
            return None

        if self._session:
            return self._session

        cookie_key = 'ssid'

        ssid = self.get_secure_cookie(cookie_key)\
            if   self._can_use_secure_cookie()\
            else self.get_cookie(cookie_key)

        if not ssid:
            ssid = self._guid_generator.generate()

            if self._can_use_secure_cookie():
                self.set_secure_cookie(cookie_key, ssid)
            else:
                self.set_cookie(cookie_key, ssid)

        self._session = SessionController(self.component('session'), ssid)

        return self._session

    def _can_use_secure_cookie(self):
        """ Check if the secure cookie is enabled.

        :rtype: boolean

        .. note::
            This only works with any classes based from :class:`tornado.webRequestHandler`
            and :class:`tornado.websocket.WebSocketHandler`.

        """
        return 'cookie_secret' in self.settings\
        and self.settings['cookie_secret']

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