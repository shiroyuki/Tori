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
from tori               import settings as ToriSettings, services as ToriService
from tori.common        import Console, Loader
from tori.exception     import *
from tori.navigation    import *
from tori.service       import ServiceEntity

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
        
        # Update the global settings.
        ToriSettings.update(self._settings)
        
        # Instantiate the backend application.
        self._backend_app = WSGIApplication(self._routes, **self._settings)
        
    def listen(self, port_number=8888):
        '''
        Tell the app to listen on the given port number.

        `port_number` is an integer to indicate which port the application should be listen to.
        This setting is however only used in a standalone mode.
        '''
        self._listening_port = port_number
        
        Console.log("Listen on port %d." % self._listening_port)
        
        return self
    
    def start(self):
        '''
        Start a server/service.
        '''
        try:
            self._backend_app.listen(self._listening_port)
            
            Console.log("Service start listening from %s." % self._base_path)
            IOLoop.instance().start()
        except KeyboardInterrupt:
            Console.log("\rCleanly stopped.")
    
    def get_listening_port(self):
        return self._listening_port

class DIApplication(Application):
    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']
    _default_services         = [
        ('renderer', 'tori.service.rendering.RenderingService', [], {})
    ]
    
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
        self._register_services()
        self._map_routing_table()
        
        # Normal procedure
        self._update_routes(self._routingMap.export())
        self._activate()
        self.listen(int(self._config.get('server port').data()))
    
    def _register_services(self):
        ''' Register services. '''
        
        # Register additional services first.
        for serviceXml in self._config.get('services > service'):
            service_id   = serviceXml.attrs['id']
            package_path = serviceXml.attrs['class']
            kwargs       = {}
            
            for param in serviceXml.get('param'):
                if not param.attrs.has_key('name') or not param.attrs['name']:
                    raise InvalidInput, 'What is the name of the parameter?'
                
                param_name = param.attrs['name']
                param_data = param.data()
                param_type = param.attrs.has_key('type') and param.attrs['type'] or None
                
                # Automatically convert data type.
                if param_type == 'class':
                    param_data = Loader(param_data).package()
                
                kwargs[param_name] = param_data
            
            self.__set_service_entity(service_id, package_path, **kwargs)
        
        # Register any missing necessary services with default configuration.
        for id, package_path, args, kwargs in self._default_services:
            self.__set_service_entity(id, package_path, *args, **kwargs)
    
    def __get_service_entity(self, id, package_path, *args, **kwargs):
        '''
        Make and return a service entity.
        
        *id* is the ID of a new service entity.
        
        *package_path* is the package path.
        
        *args* and *kwargs* are parameters used to instantiate the service.
        '''
        loader = Loader(package_path)
        entity = ServiceEntity(id, loader, *args, **kwargs)
        
        return entity
    
    def __set_service_entity(self, id, package_path, *args, **kwargs):
        '''
        Set the given service entity.
        
        *id* is the ID of a new service entity.
        
        *package_path* is the package path.
        
        *args* and *kwargs* are parameters used to instantiate the service.
        '''
        
        if ToriService.has(id):
            return
        
        ToriService.set(id, self.__get_service_entity(id, package_path, *args, **kwargs))
    
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
        
        # Create a route by type.
        if routing_type == 'controller':
            actual_route = DynamicRoute(route)
        elif routing_type == 'resource':
            actual_route = StaticRoute(route, self._base_path)
        elif routing_type == 'redirection':
            actual_route = RelayRoute(route)
        elif routing_type == 'proxy':
            raise FutureFeatureException, 'Routing a proxy is yet supported at the moment.'
            
        if not actual_route:
            raise UnknownRoutingTypeError, routing_type
        
        return actual_route
    
    def __register_route(self, route):
        routing_pattern = Route.get_pattern(route)
        
        if routing_pattern in self._registered_routes:
            raise DuplicatedRouteError
            
        self._registered_routes.append(routing_pattern)
            
            
