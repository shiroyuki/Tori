import json

from tornado.autoreload import watch
from tornado.ioloop     import IOLoop
from tornado.web        import Application as BaseApplication, URLSpec
import yaml

from .handler import PingHandler, RequestHandler


class Application(object):
    def __init__(self, port = None, debug = False, address = None):
        self._debug   = debug
        self._app     = None
        self._address = address or '0.0.0.0'
        self._port    = port    or 8000
        self._routes  = {}

    @property
    def app(self):
        """ The internal application instance.

            ..note:: This is the tornado application instance.
        """
        if not self._app:
            self.initialize()

        return self._app

    def initialize(self):
        """ Initialize the application. """
        if self._app:
            return

        self.route('/ping', PingHandler, 'ping')

        routes = sorted(
            [
                route
                for route in self._routes.values()
            ],
            key = lambda route: route._path
        )

        self._app = BaseApplication(routes, debug = self._debug)
        self._app.listen(self._port, self._address)

    def enable_debug_mode(self):
        """ Enable the debug mode """
        self._debug = True

    def bind(self, target_address : int):
        """ Define the bind IP address. """
        assert isinstance(target_address, str), 'The bind address must be a string.'

        self._address = target_address

    def listen(self, target_port : int):
        """ Define the listening port. """
        assert isinstance(target_port, int), 'The port number must be an integer.'

        self._port = target_port

    def run(self):
        """ Run the web service in a blocking mode. """
        self.initialize()

        try:
            IOLoop.current().start()
        except KeyboardInterrupt:
            pass

    def route(self, pattern : str, handler : callable, name : str = None):
        """ Set a route by pattern. """
        spec = {
            'pattern' : pattern,
            'handler' : handler,
            'name'    : name,
        }

        if issubclass(handler, RequestHandler):
            spec['kwargs'] = {
                'core' : self._core,
            }

        self._routes[pattern] = URLSpec(**spec)

    def watch(self, file_path):
        """ Put the file on observation. """
        watch(file_path)

    def __call__(self, *args, **kwargs):
        return self.app(*args, **kwargs)
