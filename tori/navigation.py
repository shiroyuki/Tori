'''
:Author: Juti Noppornpitaks
:Purpose: Internal Use Only

The navigation module is designed specifically for the dependency-injectable Application.

Please note that the term *DOMElement* used on this page denotes any of :class:`yotsuba.kotoba.Kotoba`,
:class:`yotsuba.kotoba.DOMElements` and :class:`yotsuba.kotoba.DOMElement`.

Additionally, the parameter *route* for any methods mentioned on this page is an instance of *DOMElement*.
'''

# Standard libraries
from os          import path

# Third-party libraries
from tornado.web import RedirectHandler

# Internal libraries
from tori.common    import get_class_reference as gcr
from tori.common    import console
from tori.exception import *

class RoutingMap(object):
    ''' Routing Map '''
    
    def __init__(self):
        self._sequence       = []
        self._map            = {}
        self._final_sequence = None
    
    def register(self, route):
        ''' Register a *route*. '''
        
        if not isinstance(route, Route):
            raise InvalidInput, "Expected a route."
        
        # Register the pattern to prevent the duplicate routing.
        if route.pattern() in self._sequence:
            raise DuplicatedRouteError
        
        self._sequence.append(route.pattern())
        
        # Register the route to the map.
        self._map[route.pattern()] = route
        
        # Reset the final sequence.
        self._final_sequence       = None
    
    def get(self, routing_pattern):
        ''' Get the route by *routing_pattern* where it is a string. '''
        
        try:
            return self._map[routing_pattern]
        except KeyError:
            raise RoutingPatternNotFoundError
    
    def export(self):
        ''' Export the route map as a list of tuple representatives. '''
        
        if not self._final_sequence:
            self._final_sequence = []
            
            for routing_pattern in self._sequence:
                self._final_sequence.append(self.get(routing_pattern).to_tuple())
        
        return self._final_sequence

class Route(object):
    ''' The abstract class representing a routing directive. '''
    
    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']
    
    def __init__(self, route):
        self._source  = route
        self._class   = None
        self._pattern = None
    
    def type():
        ''' Get the routing type. '''
        return self.source().name
    
    def source(self):
        ''' Get the original data for the route. '''
        return self._source
    
    def pattern(self):
        ''' Get the routing pattern. '''
        if not self._pattern:
            self._pattern = Route.get_pattern(self._source)
        
        return self._pattern
    
    def bean_class(self):
        '''
        Get the class reference for the route.
        
        .. warning::
           This method is primarily used to register a class reference to
           the routing list when the :class:`tori.application.Application`
           instantiates an instance of :class:`tornado.Application` as a
           backend application, and used for testing.
        '''
        if not self._class and self.source().attrs.has_key('class'):
            self._class = gcr(self.source().attrs['class'])
        
        return self._class
    
    @staticmethod
    def get_type(route):
        ''' Get the routing type for a given *route*. '''
        if route.name not in Route._registered_routing_types:
            raise RoutingTypeNotFoundError
        
        return route.name
    
    @staticmethod
    def get_pattern(route):
        ''' Get the routing pattern for a given *route*. '''
        if not route.attrs.has_key('pattern'):
            raise RoutingPatternNotFoundError
            
        return route.attrs['pattern']

class DynamicRoute(Route):
    ''' Dynamic route based on class Route handled by a controller. '''
    
    def __init__(self, route):
        super(self.__class__, self).__init__(route)
        
        self._controller = None
    
    def controller(self):
        ''' Get the controller. '''
        if not self._controller:
            self._controller = self.bean_class()
        
        return self._controller
        
    def to_tuple(self):
        ''' Convert the route to tuple. '''
        return (self.pattern(), self.controller())

class StaticRoute(Route):
    '''
    Static routing directive based on :class:`Route` handled by a resource controller
        
    *base_path* is a string indicating the base path for the static resource.
    '''
    
    _base_path       = None
    _default_service = None
    
    def __init__(self, route, base_path):
        super(self.__class__, self).__init__(route)
        
        self._location = None
        
        if not self._base_path:
            self._base_path = base_path
        
        # Map the routing pattern to the actual location.
        try:
            self.service().add_pattern(self.pattern(), self.location(), self.cache_enabled())
        except Exception, e:
            console.warn('Cannot register the pattern for static resource because:\n-- %s.' % e.message)
    
    def location(self):
        ''' Get the location of the static resource/content. '''
        
        if not self.source().attrs.has_key('location'):
            raise InvalidControllerDirectiveError, "The location of the resource is missing."
        
        if not self._location:
            self._location = self.source().attrs['location']
            
            secondary_location = path.join(self._base_path, self._location)
            
            # If the path of the resource is not an absolute path, treat the path as a relative path.
            if self._location[0] != '/' and path.exists(secondary_location):
                self._location = secondary_location
        
        return self._location
    
    def cache_enabled(self):
        ''' Check whether the caching option is enabled. '''
        
        return self.source().attrs.has_key('cache')\
            and self.source().attrs['cache']\
            or False
    
    def service(self):
        ''' Get the resource service. '''
        
        if not self._default_service:
            self._default_service = gcr('tori.controller.ResourceService')
        
        # Get an alternative service if specified.
        service = self.bean_class() or self._default_service
        
        return service
    
    def to_tuple(self):
        ''' Convert the route to tuple. '''
        return (self.pattern(), self.service())

class RelayRoute(Route):
    ''' Relay routing directive based on :class:`Route` used for redirection '''
    
    def __init__(self, route):
        super(self.__class__, self).__init__(route)
        
        self._destination = None
    
    def is_permanent(self):
        ''' Check whether the relay route is permanent. '''
        return self.source().attrs.has_key('permanent')\
            and self.source().attrs['permanent']\
            or False
    
    def destination(self):
        ''' Get the relaying destination. '''
        
        if not self._destination:
            try:
                self._destination = self.source().attrs['destination']
            except KeyError:
                raise InvalidControllerDirectiveError, "The destination is missing."
        
        return self._destination
    
    def to_tuple(self):
        ''' Convert the route to tuple. '''
        
        return (
            self.pattern(),
            RedirectHandler, {
                'url':       self.destination(),
                'permanent': self.is_permanent()
            }
        )
