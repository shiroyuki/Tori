import unittest

from tori.application import Application, WSGIApplication
from tori.navigation  import *

class TestDependencyInjectableApplicationClass(unittest.TestCase):
    ''' Test a dependency-injectable Application class. '''
    
    def setUp(self):
        self.app = Application('../data/good_server.xml')
    
    def tearDown(self):
        del self.app
    
    def __test_route(self, routing_pattern, routing_class):
        self.assertIsInstance(self.app.get_route(routing_pattern), routing_class, 'Check for the route of type %s' % routing_class.__name__)
    
    def test_listening_port_from_configuration_file(self):
        ''' Test the listening port from the configuration file. '''
        self.assertEqual(self.app.get_listening_port(), 1234)
    
    def test_listening_port_after_manual_intervention(self):
        ''' Test the listening port from the manual intervention (covering the abstract application class). '''
        self.app.listen(5678)
        
        self.assertEqual(self.app.get_listening_port(), 5678)
    
    def test_routing(self):
        ''' Test the registered routes. '''
        self.__test_route('/plain',              DynamicRoute)
        self.__test_route('/ctrl-with-renderer', DynamicRoute)
        self.__test_route('/resources(/.*)',     StaticRoute)
        self.__test_route('/about-shiroyuki',    RelayRoute)
        
        try:
            self.app.get_route('/plain/')
            self.assertTrue(False, 'Unexpectedly know the unregistered pattern.')
        except RoutingPatternNotFoundError:
            pass
    
    def test_mandatory_dependencies(self):
        ''' Test for mandatory dependencies required by Tori.Application '''
        self.assertEqual(self.app._hierarchy_level, 2)
        self.assertIsInstance(self.app._routing_map, RoutingMap)
        
        wsgi_app = WSGIApplication('../data/good_server.xml')
        self.assertEqual(wsgi_app._hierarchy_level, 3)
        
