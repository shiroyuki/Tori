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
from os          import path

# Third-party libraries
from imagination.loader import Loader
from kotoba.kotoba      import Kotoba
from tornado.web        import RedirectHandler

# Internal libraries
from .exception import *

class RoutingMap(object):
    """ Routing Map """

    def __init__(self):
        self._sequence       = []
        self._map            = {}
        self._final_sequence = None

    def map(self):
        return self._map

    def register(self, route, force_action=False):
        """ Register a *route*. """

        if not isinstance(route, Route):
            raise InvalidInput, "Expected a route."

        # Register the pattern to prevent the duplicate routing.
        if not force_action and route.pattern() in self._sequence:
            raise DuplicatedRouteError

        if route.pattern() not in self._sequence:
            self._sequence.append(route.pattern())

        # Register the route to the map.
        self._map[route.pattern()] = route

        # Reset the final sequence.
        self._final_sequence = None

    def get(self, routing_pattern):
        """ Get the route by *routing_pattern* where it is a string. """

        try:
            return self._map[routing_pattern]
        except KeyError:
            raise RoutingPatternNotFoundError

    def export(self):
        """ Export the route map as a list of tuple representatives. """

        if not self._final_sequence:
            self._final_sequence = []

            for routing_pattern in self._sequence:
                self._final_sequence.append(self.get(routing_pattern).to_tuple())

        return self._final_sequence

    def update(self, other):
        for route in other.map().values():
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
    """
    The abstract class representing a routing directive.

    :param route: an instance of :class:`kotoba.kotoba.Kotoba` representing the route.
    """

    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']

    def __init__(self, route_data):
        self._source  = route_data
        self._class   = None
        self._pattern = None

    def type():
        """ Get the routing type. """
        return self.source().name()

    def source(self):
        """ Get the original data for the route. """
        return self._source

    def pattern(self):
        """ Get the routing pattern. """
        if not self._pattern:
            self._pattern = Route.get_pattern(self._source)

        return self._pattern

    def bean_class(self):
        """
        Get the class reference for the route.
        """
        if not self._class and self.source().attribute('class'):
            self._class = Loader(self.source().attribute('class')).package

        return self._class

    @staticmethod
    def make(route_data, base_path=None):
        if not isinstance(route_data, Kotoba):
            raise InvalidInput

        route = None
        kind  = Route.get_type(route_data)

        # Create a route by type.
        if kind == 'controller':
            route = DynamicRoute(route_data)
        elif kind == 'resource' and base_path:
            route = StaticRoute(route_data, base_path)
        elif kind == 'resource' and not base_path:
            raise InvalidInput, 'base_path is not provided.'
        elif kind == 'redirection':
            route = RelayRoute(route_data)
        elif kind == 'proxy':
            raise FutureFeatureException, 'Routing a proxy is yet supported at the moment.'

        if not route:
            raise UnknownRoutingTypeError, kind

        return route

    @staticmethod
    def get_type(route_data):
        """ Get the routing type for a given *route*. """
        if route_data.name() not in Route._registered_routing_types:
            raise RoutingTypeNotFoundError

        return route_data.name()

    @staticmethod
    def get_pattern(route_data):
        """ Get the routing pattern for a given *route*. """
        if not route_data.attribute('pattern'):
            raise RoutingPatternNotFoundError

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
        return (self.pattern(), self.controller())

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
        self.service().add_pattern(self.pattern(), self.location(), self.cache_enabled())

    def location(self):
        """ Get the location of the static resource/content. """

        if not self.source().attribute('location'):
            raise InvalidControllerDirectiveError, "The location of the resource is missing."

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

        if not self._default_service:
            self._default_service = Loader('tori.controller.ResourceService').package

        # Get an alternative service if specified.
        service = self.bean_class() or self._default_service

        return service

    def to_tuple(self):
        """ Convert the route to tuple. """
        return (self.pattern(), self.service())

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
            raise InvalidControllerDirectiveError, "The destination is missing."

        return self._destination

    def to_tuple(self):
        """ Convert the route to tuple. """

        return (
            self.pattern(),
            RedirectHandler, {
                'url':       self.destination(),
                'permanent': self.is_permanent()
            }
        )
