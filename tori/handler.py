from tornado.web import RequestHandler as BaseRequestHandler


class UninitializedHandlerError(RuntimeError):
    """ Uninitialized Handler Error """


class PingHandler(BaseRequestHandler):
    def get(self):
        self.finish()


class RequestHandler(BaseRequestHandler):
    """ Request Handler

        This is an upgrade version of :class:`tornado.web.RequestHandler` with
        an integration with Gallium and Imagination framework. Note that the
        method :method:`tori.handler.RequestHandler` overrides the parent class
        for the framework integration.
    """
     # pylint: disable=arguments-differ
    def initialize(self, core):
        self._core = core
    # pylint: enable=arguments-differ

    def use(self, service_id):
        """ Retrieve the service by service ID """
        if not hasattr(self, '_core'):
            raise UninitializedHandlerError('The core is not provided.')

        return self._core.get(service_id)
