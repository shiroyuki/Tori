# Standard libraries
from os          import path

# Third-party libraries
from tornado.web import RedirectHandler

# Internal libraries
from tori.common    import get_class_reference as gcr
from tori.common    import console
from tori.exception import *

'''
The navigation module is designed specifically for the dependency-injectable Application.
'''

class RoutingMap(object):
    def __init__(self):
        self._sequence       = []
        self._map            = {}
        self._final_sequence = None
    
    def register(self, route):
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
        try:
            return self._map[routing_pattern]
        except KeyError:
            raise RoutingPatternNotFoundError
    
    def export(self):
        if not self._final_sequence:
            self._final_sequence = []
            
            for routing_pattern in self._sequence:
                self._final_sequence.append(self.get(routing_pattern).to_tuple())
        
        return self._final_sequence

class Route(object):
    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']
    
    def __init__(self, route):
        '''
        The abstract class for a route.
        '''
        self._source  = route
        self._class   = None
        self._pattern = None
    
    def type():
        return self.source().name
    
    def source(self):
        return self._source
    
    def pattern(self):
        if not self._pattern:
            self._pattern = Route.get_pattern(self._source)
        
        return self._pattern
    
    def bean_class(self):
        ''' Get the class of the route. '''
        if not self._class and self.source().attrs.has_key('class'):
            self._class = gcr(self.source().attrs['class'])
        
        return self._class
    
    @staticmethod
    def get_type(route):
        if route.name not in Route._registered_routing_types:
            raise RoutingTypeNotFoundError
        
        return route.name
    
    @staticmethod
    def get_pattern(route):
        if not route.attrs.has_key('pattern'):
            raise RoutingPatternNotFoundError
            
        return route.attrs['pattern']

class DynamicRoute(Route):
    def __init__(self, route):
        '''
        Dynamic route based on class Route handled by a controller.
        
        `base_path` is the base path for the resource.
        '''
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
    _base_path       = None
    _default_service = None
    
    def __init__(self, route, base_path):
        '''
        Static route based on class Route handled by a resource controller
        
        `base_path` is the base path for the resource.
        '''
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
        return self.source().attrs.has_key('cache') and self.source().attrs['cache'] or False
    
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
    def __init__(self, route):
        '''
        Dynamic route based on class Route handled by a controller.
        
        `base_path` is the base path for the resource.
        '''
        super(self.__class__, self).__init__(route)
        
        self._destination = None
    
    def is_permanent(self):
        ''' Check whether the relay route is permanent. '''
        return self.source().attrs.has_key('permanent') and self.source().attrs['permanent'] or False
    
    def destination(self):
        if not self._destination:
            if not self.source().attrs.has_key('destination'):
                raise InvalidControllerDirectiveError, "The destination is missing."
            
            self._destination = self.source().attrs['destination']
        
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
