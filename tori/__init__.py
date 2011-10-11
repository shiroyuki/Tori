import os
from tornado.ioloop import IOLoop
from tornado.web import Application as WSGIApplication
from tornado.web import StaticFileHandler

class Application(object):
    def __init__(self, controller_routing_table, static_routing_table=[], **settings):
        self.__settings = settings
        self.__static_settings = dict(path=settings['static_path'])
        self.__routing_table = []
        for pattern, handler in controller_routing_table.iteritems():
            self.__routing_table.append((pattern, handler))
        for pattern in static_routing_table:
            self.__routing_table.append((pattern, StaticFileHandler, self.__static_settings))
        self.__backend_app = WSGIApplication(self.__routing_table, **settings)
    
    def listen(self, port_number=8888):
        print "Listening on port 8888."
        self.__backend_app.listen(port_number)
    
    def start(self):
        try:
            print "Service started."
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print "\rCleanly stopped."
