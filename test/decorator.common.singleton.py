import bootstrap
import unittest

from tori.decorator.common import *

class TestSingletonClass(unittest.TestCase):
    ''' Test the 'singleton' decorator. '''
    class DummyTest(object):
        def __init__(self):
            self.__number = 0
        def take_action(self):
            self.__number += 1
        def get_number(self):
            return self.__number
    def test_positive_without_instance_attr(self):
        ''' Test if the target class without a singleton attribute. '''
        try:
            @singleton
            class PositiveTestWithoutInstanceAttr(TestSingletonClass.DummyTest): pass
            self.assertTrue(True, 'Singleton Class: Passed the initialization as expected.')
        except SingletonInitializationException:
            self.assertTrue(False, 'Singleton Class: Failed the initialization with known exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
        # Test for the type.
        self.assertIsInstance(PositiveTestWithoutInstanceAttr.instance(), PositiveTestWithoutInstanceAttr)
        # Test if it is working. (case #1)
        PositiveTestWithoutInstanceAttr.instance().take_action()
        self.assertEqual(PositiveTestWithoutInstanceAttr.instance().get_number(), 1)
        # Test if it is working. (case #n)
        PositiveTestWithoutInstanceAttr.instance().take_action()
        self.assertEqual(PositiveTestWithoutInstanceAttr.instance().get_number(), 2)
    
    def test_negative_with_null_instance_attr(self):
        ''' Test if the target class with null singleton attribute. '''
        try:
            @singleton
            class NegativeTestWithNullInstanceAttr(TestSingletonClass.DummyTest):
                _singleton_instance = None
                def __init__(self):
                    # Use `self.__class__` to call the parent class' constructor.
                    super(self.__class__, self).__init__()
            self.assertTrue(False, 'Singleton Class: Passed the initialization unexpectedly.')
        except SingletonInitializationException:
            self.assertTrue(True, 'Singleton Class: Failed the initialization with expected exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
    
    def test_negative_with_unexpected_instance_attr(self):
        ''' Test if the target class has already had an attribute `_singleton_instance` but it is not compatible. '''
        try:
            @singleton
            class NegativeTestWithUnexpectedInstanceAttr(TestSingletonClass.DummyTest):
                _singleton_instance = {}
                def __init__(self):
                    # Use `self.__class__` to call the parent class' constructor.
                    super(self.__class__, self).__init__()
            self.assertTrue(False, 'Singleton Class: Passed the initialization unexpectedly.')
        except SingletonInitializationException:
            self.assertTrue(True, 'Singleton Class: Failed the initialization with expected exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
            

if __name__ == '__main__':
    unittest.main()