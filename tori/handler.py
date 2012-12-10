"""
Common Handler
==============

:Author: Juti Noppornpitak
:Status: Stable, Internal Only
:Last Update: |today|

This module contains code commonly used by request handlers and web socket handlers.
"""

from tori.centre             import services
from tori.session.generator  import GuidGenerator
from tori.session.controller import Controller

class Handler(object):
    _guid_generator = GuidGenerator()

    def __init__(self):
        """
        Handler Decorator Class used with Tornado's Handler-based classes

        .. note:: This should be moved to Controller and WebSocket.
        """
        self._session = None

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
                self.set_secure_cookie(cookie_key, ssid, expires_days=1)
            else:
                self.set_cookie(cookie_key, ssid, expires_days=1)

        self._session = Controller(self.component('session'), ssid)

        return self._session

    def _can_use_secure_cookie(self):
        """
        Check if the secure cookie is enabled.

        :rtype: boolean

        .. note::
            This only works with any classes based from :class:`tornado.webRequestHandler`
            and :class:`tornado.websocket.WebSocketHandler`.

        """
        return 'cookie_secret' in self.settings\
            and self.settings['cookie_secret']