import os
import sys

from tornado.ioloop import IOLoop
from tornado.web import Application as WSGIApplication
from tornado.web import StaticFileHandler

class Application(object):
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
        
        # Register the routes to controllers.
        for pattern, handler in controller_routing_table.iteritems():
            __route = (pattern, handler)
            self.__routing_table.append(__route)
        
        # Register the routes to static content.
        for pattern in static_routing_table:
            __route = (pattern, StaticFileHandler, self.__static_settings)
            self.__routing_table.append(__route)
        
        self.__backend_app = WSGIApplication(self.__routing_table, **settings)
    
    def listen(self, port_number=8888):
        '''
        Tell the app to listen on the given port number.

        `port_number` is an integer to indicate which port the application should be listen to.
        This setting is however only used in a standalone mode.
        '''
        self.__backend_app.listen(port_number)
        return self
    
    def start(self):
        '''
        Start a server/service.
        '''
        try:
            print "Service started from %s." % self.__base_path
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print "\rCleanly stopped."
