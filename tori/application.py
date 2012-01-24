import os
import re
import sys

# Kotoba 2.x from Yotsuba 3.1 will be replaced by Kotoba 3.0 as soon as the official release is available.
from yotsuba.lib.kotoba import Kotoba

from tornado.ioloop     import IOLoop
from tornado.web        import Application as WSGIApplication
from tornado.web        import RedirectHandler
from tornado.web        import StaticFileHandler

from tori.exception     import *

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
        current_function = sys._getframe(self._hierarchy_level)
        caller_function = current_function.f_code
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
    def __init__(self, configuration_location, **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado framework.

        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        '''
        self._hierarchy_level = 2
        super(self.__class__, self).__init__(**settings)
        self._config = Kotoba(os.path.join(self._base_path, configuration_location))
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
                    <route type="controller" pattern="/">app.controller.MainController</route>
                    <!--
                        Example for static content
                        
                        Please note that the content of route of this type can be a relative
                        path, a full path or blank. If it is blank, it will look into a folder
                        called `static` living at the same location as the WSGI/server script.
                        
                        This should be only used for development only.
                    -->
                    <route type="controller" pattern="/resources/(.*)">resources</route>
                    <!-- Example for redirection -->
                    <route type="redirection"
                           pattern="/about-shiroyuki"
                           permanent="False"
                    >http://shiroyuki.com</route>
                </routes>
            </application>
        
        This is a pseudo protected method, which is triggered automatically on instantiation and
        should not be used directly as it takes no effect unless it is used with `_update_routes`.
        and reactivate the application with `_activate`.
        '''
        routes                      = []
        registered_routing_patterns = []
        
        # Register the routes to controllers.
        for config in self._config.get('routes route'):
            if not config.attrs.has_key('type'):
                raise RoutingTypeNotFoundError
            
            routing_type = config.attrs['type']
            
            if not config.attrs.has_key('pattern'):
                raise RoutingPatternNotFoundError
            
            routing_pattern = config.attrs['pattern']
            
            if routing_pattern in registered_routing_patterns:
                raise DuplicatedRouteError
            
            registered_routing_patterns.append(routing_pattern)
            
            route = None
            
            # Create a route by type.
            if routing_type == 'controller':
                # Gather information
                controller_path = config.data()
                access_path     = re.split('\.', controller_path)
                module_name     = '.'.join(access_path[:-1])
                controller_name = access_path[-1]
                
                # Automatically import the controller (or handler).
                __import__(module_name, fromlist=[controller_name])
                
                # Get the controller.
                controller      = getattr(sys.modules[module_name], controller_name)
                
                # Create a route for a controller.
                route = (routing_pattern, controller)
            elif routing_type == 'static':
                # Create a route for a static content / resource.
                route = (routing_pattern, StaticFileHandler, self._static_routing_setting)
            elif routing_type == 'redirection':
                # Gather information
                destination = config.data()
                
                if not config.attrs.has_key('permanent'):
                    raise InvalidRedirectionDirectiveError, "Missing permanent parameter."
                
                is_permanent = bool(config.attrs['permanent'])
                
                # Create a route for a redirection directive.
                route = (
                    routing_pattern,
                    RedirectHandler, {
                        'url':       destination,
                        'permanent': is_permanent
                    }
                )
            
            if not route:
                raise UnknownRoutingTypeError, routing_type
            
            routes.append(route)
        
        return routes
