# Standard libraries
import os
import re
import sys

# Third-party libraries
# Kotoba 2.x from Yotsuba 3.1 will be replaced by Kotoba 3.0 as soon as the official release is available.
from   imagination.entity import Entity  as ImaginationEntity
from   imagination.loader import Loader  as ImaginationLoader
from   kotoba             import load_from_file
from   tornado.ioloop     import IOLoop
from   tornado.web        import Application as OriginalApplication
import tornado.web
from   tornado.wsgi       import WSGIApplication as OriginalWSGIApplication
from   wsgiref            import handlers

# Internal libraries
from .centre     import settings as AppSettings
from .centre     import services as AppServices
from .common     import Console
from .exception  import *
from .navigation import *

class Application(object):
    '''
    Interface to bootstrap a WSGI application with Tornado framework. This is the basic
    application class which do nothing. Please don't use this directly.
        
    `settings` is a dictionary of extra settings to Tornado engine. For more information,
    please consult with Tornado documentation.
    '''
    
    def __init__(self, **settings):
        self._hierarchy_level = len(self.__class__.__mro__) - 1
        
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
        
        self._settings['base_path'] = self._base_path
        
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
        AppSettings.update(self._settings)
        
        # Instantiate the backend application.
        self._backend_app = OriginalApplication(self._routes, **self._settings)
        
    def listen(self, port_number=8888):
        '''
        Tell the app to listen on the given port number.

        `port_number` is an integer to indicate which port the application should be listen to.
        This setting is however only used in a standalone mode.
        '''
        
        self._listening_port = int(port_number)
        
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
    
    def get_backbone(self):
        return self._backend_app
    
    def get_listening_port(self):
        return self._listening_port

class DIApplication(Application):
    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']
    _default_services         = [
        ('finder', 'tori.common.Finder', [], {}),
        ('renderer', 'tori.service.rendering.RenderingService', [], {})
    ]
    
    def __init__(self, configuration_location, **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado built-in server.

        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        '''
        Application.__init__(self, **settings)
        
        self._config            = load_from_file(os.path.join(self._base_path, configuration_location))
        self._routingMap        = RoutingMap()
        self._settings['debug'] = self._config.find('server debug').data().lower() == 'true'
        self._port              = self._config.find('server port').data()
        
        if settings.has_key('port'):
            self._port = settings['port']
            Console.log('New listening port: %s' % self._port)
        
        # Exclusive procedure
        self._register_services()
        self._map_routing_table()
        
        # Map the error handler.
        delegate = self._config.find('server error').data()
        
        if delegate:
            Console.log('Custom Error Handler: %s' % delegate)
            tornado.web.ErrorHandler = ImaginationLoader(delegate).package()
        
        # Normal procedure
        self._update_routes(self._routingMap.export())
        self.listen(self._port)
        self._activate()
    
    def _register_services(self):
        ''' Register services. '''
        
        # Register any missing necessary services with default configuration.
        for id, package_path, args, kwargs in self._default_services:
            self._set_service_entity(id, package_path, *args, **kwargs)
        
        service_block = self._config.children('service')
        
        service_config_path = service_block and service_block.data() or None
        
        if service_config_path:
            config_filepath = os.path.join(self._base_path, service_config_path)
            AppServices.load_xml(config_filepath)
    
    def _make_service_entity(self, id, package_path, *args, **kwargs):
        '''
        Make and return a service entity.
        
        *id* is the ID of a new service entity.
        
        *package_path* is the package path.
        
        *args* and *kwargs* are parameters used to instantiate the service.
        '''
        loader = ImaginationLoader(package_path)
        entity = ImaginationEntity(id, loader, *args, **kwargs)
        
        return entity
    
    def _set_service_entity(self, id, package_path, *args, **kwargs):
        '''
        Set the given service entity.
        
        *id* is the ID of a new service entity.
        
        *package_path* is the package path.
        
        *args* and *kwargs* are parameters used to instantiate the service.
        '''
                
        AppServices.set(id, self._make_service_entity(id, package_path, *args, **kwargs))
    
    def get_route(self, routing_pattern):
        ''' Get the route. '''
        return self._routingMap.get(routing_pattern)
    
    def _map_routing_table(self):
        '''
        Map a routing table based on the configuration.
        
        Suppose the controller is `app.controller.MainController` the configuration is as followed:
        
            <application>
                <!-- ... -->
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
                <!-- ... -->
            </application>
        
        This is a pseudo protected method, which is triggered automatically on instantiation and
        should not be used directly as it takes no effect unless it is used with `_update_routes`.
        and reactivate the application with `_activate`.
        '''
        routing_sequence = self._config.children('routes')
        
        if not routing_sequence:
            return
        
        # Register the routes to controllers.
        for route in routing_sequence[0].children():
            self._routingMap.register(
                self._analyze_route(route)
            )
    
    def _analyze_route(self, route):
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

class WSGIApplication(DIApplication):
    def __init__(self, configuration_location, **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado framework.

        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        '''
        
        DIApplication.__init__(self, configuration_location, **settings)
    
    def _activate(self):
        '''
        Activate the backend application.
        '''
        
        # Update the global settings.
        AppSettings.update(self._settings)
        
        # Instantiate the backend application.
        self._backend_app = OriginalWSGIApplication(self._routes, **self._settings)

    def start(self):
        handlers.CGIHandler().run(self.get_backbone())
