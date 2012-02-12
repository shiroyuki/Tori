import unittest

from tori.application import DIApplication
from tori.navigation  import *

class TestDependencyInjectableApplicationClass(unittest.TestCase):
    ''' Test a dependency-injectable Application class. '''
    
    def setUp(self):
        self.app = DIApplication('../data/good_server.xml')
    
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

if __name__ == '__main__':
    unittest.main()
