import os
import sys

from yotsuba.lib.kotoba import Kotoba

from tornado.ioloop     import IOLoop
from tornado.web        import Application as WSGIApplication
from tornado.web        import StaticFileHandler

class Application(object):
    def __init__(self, **settings):
        '''
        Interface to bootstrap a WSGI application with Tornado framework.
        
        `settings` is a dictionary of extra settings to Tornado engine. For more information,
        please consult with Tornado documentation.
        '''
        
        # Setting for the application.
        self._settings = settings
        
        # Get the reference to the calling function
        current_function = sys._getframe(2)
        caller_function = current_function.f_code
        reference_to_caller = caller_function.co_filename
        
        # Base path
        self._base_path = os.path.abspath(os.path.dirname(os.path.abspath(reference_to_caller)))
        self._base_path = 'static_path' in settings and settings['static_path'] or self._base_path
        
        self._static_routing_setting = dict(path=self._base_path)
        self._routes = []
    
    def _update_routes(self, routes):
        self._routes = routes
    
    def _activate(self):
        print 'Framework activated.'
        self._backend_app = WSGIApplication(self._routes, **self._settings)
        
    def listen(self, port_number=8888):
        '''
        Tell the app to listen on the given port number.

        `port_number` is an integer to indicate which port the application should be listen to.
        This setting is however only used in a standalone mode.
        '''
        self._backend_app.listen(port_number)
        print "Changed the listening port to %d." % port_number
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
        '''
        super(self.__class__, self).__init__(**settings)
        self._update_routes(
            self.__map_routing_table(
                controller_routing_table, static_routing_table
            )
        )
        self._activate()
    
    def __map_routing_table(self, controller_routing_table, static_routing_table):
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
        
        # Setting for the application.
        self.__settings = settings
        
        # Get the reference to the calling function
        current_function = sys._getframe(1)
        caller_function = current_function.f_code
        reference_to_caller = caller_function.co_filename
        
        # Base path
        self.__base_path = os.path.abspath(os.path.dirname(os.path.abspath(reference_to_caller)))
        self.__base_path = 'static_path' in settings and settings['static_path'] or self.__base_path
        
        # Static settings for routing static content
        self.__static_settings = dict(path=self.__base_path)
        
        # Master routing table
        self.__routing_table = []
        self.__map_routing_table(configuration_location)
        
        self.__backend_app = WSGIApplication(self.__routing_table, **settings)
        
    def __map_routing_table(self, configuration_location):
        selector = Kotoba(configuration_location)
        
        # Register the routes to controllers.
        for pattern, controller_name in controller_routing_table.iteritems():
            controller = eval(controller_name)
            __route = (pattern, controller)
            self.__routing_table.append(__route)
        
        # Register the routes to static content.
        #for pattern in static_routing_table:
        #    __route = (pattern, StaticFileHandler, self.__static_settings)
        #    self.__routing_table.append(__route)
