import os
import re
import sys

# Kotoba 2.x from Yotsuba 3.1 will be replaced by Kotoba 3.0 as soon as the official release is available.
from yotsuba.lib.kotoba import Kotoba

from tornado.ioloop     import IOLoop
from tornado.web        import Application as WSGIApplication
from tornado.web        import RedirectHandler
from tornado.web        import StaticFileHandler

from tori.common           import get_class_reference as gcr
from tori.decorator.common import _make_a_singleton_class as make_a_singleton_class
from tori.exception        import *

class Application(object):
    def __init__(self, **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado framework.
        
        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        '''
        if not self._hierarchy_level:
            self._hierarchy_level = 1
        
        # Setting for the application.
        self._settings = settings
        
        # Get the reference to the calling function
        current_function    = sys._getframe(self._hierarchy_level)
        caller_function     = current_function.f_code
        reference_to_caller = caller_function.co_filename
        
        # Base path
        self._base_path = os.path.abspath(os.path.dirname(os.path.abspath(reference_to_caller)))
        self._base_path = 'static_path' in settings and settings['static_path'] or self._base_path
        
        self._static_routing_setting = dict(path=self._base_path)
        self._routes = []
    
    def _update_routes(self, routes):
        '''
        Update the routes.
        
        `routes` is the list of routes. See Tornado documentation on `tornado.web.Application` for more detail.
        '''
        self._routes = routes
    
    def _activate(self):
        '''
        Activate the backend application.
        '''
        self._backend_app = WSGIApplication(self._routes, **self._settings)
        
    def listen(self, port_number=8888):
        '''
        Tell the app to listen on the given port number.

        `port_number` is an integer to indicate which port the application should be listen to.
        This setting is however only used in a standalone mode.
        '''
        self._backend_app.listen(port_number)
        print "Listen on port %d." % port_number
        return self
    
    def start(self):
        '''
        Start a server/service.
        '''
        try:
            print "Service start listening from %s." % self._base_path
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print "\rCleanly stopped."

class SimpleApplication(Application):
    def __init__(self, controller_routing_table, static_routing_table=[], **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado framework.
        
        `controller_routing_table` is a routing table for controllers, proxy or redirection.
        The current implementation is based on Tornado's routing. The future release will be
        based on a configuration file (preferably as an XML or YAML file).

        `static_routing_table` is a routing table for static content. The future release
        will enforce the routing from the configuration file.

        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        
        This interface doesn't support redirection and proxy.
        '''
        self._hierarchy_level = 2
        super(self.__class__, self).__init__(**settings)
        self._update_routes(
            self._map_routing_table(
                controller_routing_table, static_routing_table
            )
        )
        self._activate()
    
    def _map_routing_table(self, controller_routing_table, static_routing_table):
        routes = []
        
        # Register the routes to controllers.
        for pattern, handler in controller_routing_table.iteritems():
            route = (pattern, handler)
            routes.append(route)
        
        # Register the routes to static content.
        for pattern in static_routing_table:
            route = (pattern, StaticFileHandler, self._static_routing_setting)
            routes.append(route)
        
        return routes
    
class DIApplication(Application):
    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']
    
    def __init__(self, configuration_location, **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado framework.

        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        '''
        self._hierarchy_level = 2
        
        super(self.__class__, self).__init__(**settings)
        
        self._config            = Kotoba(os.path.join(self._base_path, configuration_location))
        self._registered_routes = []
        
        self._update_routes(self._map_routing_table())
        self._activate()
        self.listen(int(self._config.get('server port').data()))
        
    def _map_routing_table(self):
        '''
        Map a routing table based on the configuration.
        
        Suppose the controller is `app.controller.MainController` the configuration is as followed:
        
            <application>
                ... <!-- Assume that there are some configurations here -->
                <routes>
                    <!-- Example for controller -->
                    <controller class="app.controller.MainController" pattern="/">
                    <!--
                        Example for static content
                        
                        Please note that the content of route of this type can be a relative
                        path, a full path or blank. If it is blank, it will look into a folder
                        called `static` living at the same location as the WSGI/server script.
                        
                        This should be only used for development only.
                    -->
                    <resource location="resources" pattern="/resources/(.*)"/>
                    <!-- Example for redirection -->
                    <redirection destination="http://shiroyuki.com" pattern="/about-shiroyuki" permanent="False"/>
                    <!-- Example for proxy -->
                    <proxy type="http://shiroyuki.com/api" pattern="/api"/>
                </routes>
            </application>
        
        This is a pseudo protected method, which is triggered automatically on instantiation and
        should not be used directly as it takes no effect unless it is used with `_update_routes`.
        and reactivate the application with `_activate`.
        '''
        routes = []
        
        # Register the routes to controllers.
        for route in self._config.get('routes > *'):
            self.__register_route(route)
            routes.append(self.__analyze_route(route))
        
        return routes
    
    def __analyze_route(self, route):
        actual_route    = None
        routing_type    = self.__get_routing_type(route)
        routing_pattern = self.__get_routing_pattern(route)
            
        # Create a route by type.
        if routing_type == 'controller':
            actual_route = self.__wire_controller(route)
        elif routing_type == 'resource':
            actual_route = self.__wire_resource(route)
        elif routing_type == 'redirection':
            actual_route = self.__issue_redirection(route)
        elif routing_type == 'proxy':
            raise FutureFeatureException
            
        if not actual_route:
            raise UnknownRoutingTypeError, routing_type
        
        return actual_route
        
    def __wire_controller(self, route):
        if not route.attrs.has_key('class'):
            raise InvalidControllerDirectiveError, "Controller class is missing."
                
        # Create a route for a controller.
        return (
            self.__get_routing_pattern(route),
            gcr(route.attrs['class'])
        )
        
    def __wire_resource(self, route):
        # Create a route for a static content / resource.
        if not route.attrs.has_key('location'):
            raise InvalidControllerDirectiveError, "Resouce location is missing."
                
        # Gather information about location, caching flag and resource service.
        routing_pattern    = self.__get_routing_pattern(route)
        actual_location    = route.attrs['location']
        cache_enabled      = route.attrs.has_key('cache') and route.attrs['cache'] or False
        secondary_location = os.path.join(self._base_path, actual_location)
        resource_service   = gcr('tori.controller.ResourceService')
                
        # If the path of the resource is not an absolute path, treat the path as a relative path.
        if actual_location[0] != '/' and os.path.exists(secondary_location):
            actual_location = secondary_location
                
        # Map the routing pattern to the actual location.
        resource_service.add_pattern(routing_pattern, actual_location, cache_enabled)
                
        return (routing_pattern, resource_service)
        
    def __issue_redirection(self, route):
        return (
            self.__get_routing_pattern(route),
            RedirectHandler, {
                'url':       route.data(),
                'permanent': route.attrs.has_key('permanent') and bool(route.attrs['permanent']) or False
            }
        )
        
    def __get_routing_type(self, route):
        if route.name not in self._registered_routing_types:
            raise RoutingTypeNotFoundError
        
        return route.name
        
    def __get_routing_pattern(self, route):
        if not route.attrs.has_key('pattern'):
            raise RoutingPatternNotFoundError
            
        return route.attrs['pattern']
        
    def __register_route(self, route):
        routing_pattern = self.__get_routing_pattern(route)
        
        if routing_pattern in self._registered_routes:
            raise DuplicatedRouteError
            
        self._registered_routes.append(routing_pattern)
            
            
