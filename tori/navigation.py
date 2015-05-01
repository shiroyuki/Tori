# -*- coding: utf-8 -*-

"""
:Author: Juti Noppornpitaks
:Purpose: Internal Use Only

The navigation module is designed specifically for the dependency-injectable Application.

Please note that the term *DOMElement* used on this page denotes any of :class:`yotsuba.kotoba.Kotoba`,
:class:`yotsuba.kotoba.DOMElements` and :class:`yotsuba.kotoba.DOMElement`.

Additionally, the parameter *route* for any methods mentioned on this page is an instance of *DOMElement*.
"""

# Standard libraries
from os import path
from re import compile as RegExp

# Third-party libraries
from imagination.loader import Loader
from kotoba.kotoba      import Kotoba
from tornado.web        import RedirectHandler

# Internal libraries
from tori.common    import get_logger
from tori.exception import *

class RoutingMap(object):
    """ Routing Map """

    _GUID = 0

    def __init__(self):
        RoutingMap._GUID += 1

        self._guid           = RoutingMap._GUID
        self._logger         = get_logger('{}.{}'.format(__name__, self.__class__.__name__))
        self._sequence       = []
        self._raw_map        = {}
        self._id_map         = {}
        self._final_sequence = None

    def register(self, route, force_action=False):
        """ Register a *route*. """

        if not isinstance(route, Route):
            raise InvalidInput("Expected a route.")

        # Register the pattern to prevent the duplicate routing.
        if not force_action and route.pattern in self._sequence:
            raise DuplicatedRouteError('The route pattern is already registered.')

        self._logger.debug('RM-{}: Registering {}...'.format(self._guid, route.pattern))

        if route.pattern in self._sequence:
            self._logger.debug('RM-{}: {} already registered'.format(self._guid, route.pattern))
            return

        self._sequence.append(route.pattern)

        # Register the route to the map.
        self._raw_map[route.pattern] = route

        # Reset the final sequence.
        self._final_sequence = None

        # Register the route to the short ID map.
        if not force_action and route.id and route.id in self._id_map:
            raise DuplicatedRouteError('The route ID "{}" is already registered.'.format(route.id))

        self._id_map[route.id] = route

        self._logger.debug('Added route for "{}"'.format(route.pattern))

    def resolve(self, id, **params):
        """ Resolve the path by ID

            :param id str: the path ID
            :param params: the variables used in the routing pattern
        """

        if id not in self._id_map:
            raise KeyError('The route ID "{}" is not registered.'.format(id))

        route = self._id_map[id]

        if route.use_regexp:
            raise RuntimeError('The route is defined with a regular expression. It cannot be resolved.')

        return route.resolvable_pattern.format(**params)

    def find_by_pattern(self, routing_pattern):
        """ Get the route by *routing_pattern* where it is a string. """

        try:
            return self._raw_map[routing_pattern]
        except KeyError:
            raise RoutingPatternNotFoundError(
                'Failed to find the route for "{lookup}" in {availables}'.format(
                    lookup = routing_pattern,
                    availables = ', '.join(self._raw_map.keys())
                )
            )

    def export(self):
        """ Export the route map as a list of tuple representatives.

        :rtype: list
        """
        if not self._final_sequence:
            has_favicon = False

            self._final_sequence = []

            self._logger.debug('RM-{}: Exporting the routing table to Tornado Application...'.format(self._guid))

            for routing_pattern in self._sequence:
                self._logger.debug('RM-{}: Exporting the route "{}"...'.format(self._guid, routing_pattern))

                if routing_pattern == '/favicon.ico':
                    has_favicon = True

                self._final_sequence.append(self.find_by_pattern(routing_pattern).to_tuple())

            if not has_favicon:
                self._logger.debug('RM-{}: Exporting the route for /favicon.ico...'.format(self._guid))
                self._final_sequence.append(('/favicon.ico', StaticRoute._default_service))

                self._logger.debug('RM-{}: Exported all routes.'.format(self._guid))

        return self._final_sequence

    def update(self, other):
        self._logger.debug('RM-{}: Updating'.format(self._guid))

        other_map = other._raw_map

        for rk in other._sequence:
            route = other_map[rk]

            self.register(route, True)

    @staticmethod
    def make(configuration, base_path=None):
        """
        Make a routing table based on the given *configuration*.

        :param `base_path`: is an optional used by :method `Route.make`:.
        """
        if not configuration:
            return

        if not isinstance(configuration, Kotoba):
            raise InvalidInput

        routing_map = RoutingMap()

        # Register the routes to controllers.
        for route_data in configuration.children():
            routing_map.register(Route.make(route_data, base_path))

        return routing_map

class Route(object):
    """The abstract class representing a routing directive.

    :param route: an instance of :class:`kotoba.kotoba.Kotoba` representing the route.
    """
    _re_wildcard_recur        = RegExp('(\*{2,})')
    _re_wildcard_non_recur    = RegExp('(\*{1})')
    _re_named_parameter       = RegExp('\{(?P<name>[^\}]+)\}')
    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']

    def __init__(self, route_data):
        self._source  = route_data
        self._class   = None
        self._pattern = Route.get_pattern(self._source)
        self._resolvable_pattern = None
        self._id      = self._source.attribute('id')

        self._use_regexp = self._source.attribute('regexp') or False

        if self._use_regexp:
            self._use_regexp = self._use_regexp.lower() == 'true'

        # If the given pattern is not a regular expression, rewrite the routing pattern.
        if not self.use_regexp:
            self._resolvable_pattern = self._pattern
            self._pattern = self._re_wildcard_recur.sub('(.+)', self._pattern)
            self._pattern = self._re_wildcard_non_recur.sub('([^/]+)', self._pattern)
            self._pattern = self._re_named_parameter.sub('(?P<\g<name>>.+)', self._pattern)

    @property
    def id(self):
        return self._id

    @property
    def use_regexp(self):
        return self._use_regexp

    @property
    def pattern(self):
        return self._pattern

    @property
    def resolvable_pattern(self):
        return self._resolvable_pattern

    def type(self):
        """ Get the routing type.

        :rtype: str
        """
        return self.source().name()

    def source(self):
        """ Get the original data for the route.

        :rtype: str
        """
        return self._source

    def bean_class(self):
        """ Get the class reference for the route.

        :rtype: type
        """
        if not self._class and self.source().attribute('class'):
            self._class = Loader(self.source().attribute('class')).package

        return self._class

    @staticmethod
    def make(route_data, base_path=None):
        if not isinstance(route_data, Kotoba):
            raise InvalidInput('')

        route = None
        kind  = Route.get_type(route_data)

        # Create a route by type.
        if kind == 'controller':
            route = DynamicRoute(route_data)
        elif kind == 'resource' and base_path:
            route = StaticRoute(route_data, base_path)
        elif kind == 'resource' and not base_path:
            raise InvalidInput('base_path is not provided.')
        elif kind == 'redirection':
            route = RelayRoute(route_data)
        elif kind == 'proxy':
            raise FutureFeatureException('Routing a proxy is yet supported at the moment.')

        if not route:
            raise UnknownRoutingTypeError(kind)

        return route

    @staticmethod
    def get_type(route_data):
        """ Get the routing type for a given *route*. """
        if route_data.name() not in Route._registered_routing_types:
            raise RoutingTypeNotFoundError('')

        return route_data.name()

    @staticmethod
    def get_pattern(route_data):
        """ Get the routing pattern for a given *route*. """
        if not route_data.attribute('pattern'):
            raise RoutingPatternNotFoundError('The pattern is not given.')

        return route_data.attribute('pattern')

class DynamicRoute(Route):
    """ Dynamic route based on class Route handled by a controller. """

    def __init__(self, route):
        super(self.__class__, self).__init__(route)

        self._controller = None

    def controller(self):
        """ Get the controller. """
        if not self._controller:
            self._controller = self.bean_class()

        return self._controller

    def to_tuple(self):
        """ Convert the route to tuple. """
        return (self.pattern, self.controller())

class StaticRoute(Route):
    """
    Static routing directive based on :class:`Route` handled by a resource controller

    :param base_path: is a string indicating the base path for the static resource.
    """
    _base_path       = None
    _default_service = None

    def __init__(self, route, base_path):
        super(self.__class__, self).__init__(route)

        self._location = None

        if not self._base_path:
            self._base_path = base_path

        # Map the routing pattern to the actual location.
        self.service().add_pattern(self.pattern, self.location(), self.cache_enabled())

    def location(self):
        """ Get the location of the static resource/content. """

        if not self.source().attribute('location'):
            raise InvalidControllerDirectiveError('The location of the resource is missing.')

        if not self._location:
            self._location = self.source().attribute('location')

            secondary_location = path.join(self._base_path, self._location)

            # If the path of the resource is not an absolute path, treat the path as a relative path.
            if self._location[0] != '/' and path.exists(secondary_location):
                self._location = secondary_location

        return self._location

    def cache_enabled(self):
        """ Check whether the caching option is enabled. """

        _cache_enabled = self.source().attribute('cache')

        return _cache_enabled and _cache_enabled.lower() == 'true' or False

    def service(self):
        """ Get the resource service. """
        service = self.bean_class() or StaticRoute.default_service()

        return service

    def to_tuple(self):
        """ Convert the route to tuple. """
        return (self.pattern, self.service())

    @staticmethod
    def default_service():
        if not StaticRoute._default_service:
            StaticRoute._default_service = Loader('tori.controller.ResourceService').package

        return StaticRoute._default_service

class RelayRoute(Route):
    """ Relay routing directive based on :class:`Route` used for redirection """

    def __init__(self, route):
        super(self.__class__, self).__init__(route)

        self._destination = None

    def is_permanent(self):
        """ Check whether the relay route is permanent. """
        _is_permanent = self.source().attribute('permanent')
        return _is_permanent and _is_permanent.lower() == 'true' or False

    def destination(self):
        """ Get the relaying destination. """

        if not self._destination:
            self._destination = self.source().attribute('destination')

        if not self._destination:
            raise InvalidControllerDirectiveError('The destination is missing.')

        return self._destination

    def to_tuple(self):
        """ Convert the route to tuple. """

        return (
            self.pattern,
            RedirectHandler, {
                'url':       self.destination(),
                'permanent': self.is_permanent()
            }
        )
