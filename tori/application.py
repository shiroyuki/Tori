# Standard libraries
import os
import re
import sys

# Third-party libraries
# Kotoba 2.x from Yotsuba 3.1 will be replaced by Kotoba 3.0 as soon as the official release is available.
from yotsuba.lib.kotoba import Kotoba
from tornado.ioloop     import IOLoop
from tornado.web        import Application as WSGIApplication
from tornado.web        import RedirectHandler

# Internal libraries
from tori.common        import console
from tori.exception     import *
from tori.navigation    import *

class Application(object):
    '''
    Interface to bootstrap a WSGI application with Tornado framework. This is the basic
    application class which do nothing. Please don't use this directly.
        
    `settings` is a dictionary of extra settings to Tornado engine. For more information,
    please consult with Tornado documentation.
    '''
    
    def __init__(self, **settings):
        if not self._hierarchy_level:
            self._hierarchy_level = 1
        
        self._number_of_activation = 0
        # Setting for the application.
        self._settings          = settings
        self._settings['debug'] = False
        
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
        self._listening_port = port_number
        console.log("Listen on port %d." % self._listening_port)
        
        return self
    
    def start(self):
        '''
        Start a server/service.
        '''
        try:
            self._backend_app.listen(self._listening_port)
            
            console.log("Service start listening from %s." % self._base_path)
            IOLoop.instance().start()
        except KeyboardInterrupt:
            console.log("\rCleanly stopped.")
    
    def get_listening_port(self):
        return self._listening_port

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
        self._routingMap        = RoutingMap()
        self._settings['debug'] = self._config.get('server debug').data()
        
        # Exclusive procedure
        self._map_routing_table()
        
        # Normal procedure
        self._update_routes(self._routingMap.export())
        self._activate()
        self.listen(int(self._config.get('server port').data()))
    
    def get_route(self, routing_pattern):
        ''' Get the route. '''
        return self._routingMap.get(routing_pattern)
    
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
        # Register the routes to controllers.
        for route in self._config.get('routes > *'):
            self._routingMap.register(
                self.__analyze_route(route)
            )
    
    def __analyze_route(self, route):
        actual_route    = None
        routing_type    = Route.get_type(route)
        routing_pattern = Route.get_pattern(route)
            
        # Create a route by type.
        if routing_type == 'controller':
            actual_route = DynamicRoute(route)
        elif routing_type == 'resource':
            actual_route = StaticRoute(route, self._base_path)
        elif routing_type == 'redirection':
            actual_route = RelayRoute(route)
        elif routing_type == 'proxy':
            raise FutureFeatureException
            
        if not actual_route:
            raise UnknownRoutingTypeError, routing_type
        
        return actual_route
    
    def __register_route(self, route):
        routing_pattern = Route.get_pattern(route)
        
        if routing_pattern in self._registered_routes:
            raise DuplicatedRouteError
            
        self._registered_routes.append(routing_pattern)
            
            
