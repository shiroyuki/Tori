import bootstrap
import unittest

from tori.decorator.common import *

class TestSingletonClass(unittest.TestCase):
    ''' Test the 'singleton' decorator. '''
    class DummyTest(object):
        def __init__(self):
            self.number = 0
        def take_action(self):
            self.number += 1
        def get_number(self):
            return self.number
    
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
    
    def test_positive_using_decorator_with_primitive_parameter(self):
        ''' Test if the target class without a singleton attribute but using a decorator with primitive perimiter. '''
        try:
            @singleton(10)
            class PositiveTestWithParameterForSI(TestSingletonClass.DummyTest):
                def __init__(self, init_number):
                    super(self.__class__, self).__init__()
                    self.number = init_number
            self.assertTrue(True, 'Singleton Class: Passed the initialization as expected.')
        except SingletonInitializationException:
            self.assertTrue(False, 'Singleton Class: Failed the initialization with known exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
        # Test for the type.
        self.assertIsInstance(PositiveTestWithParameterForSI.instance(), PositiveTestWithParameterForSI)
        # Test if it is working. (case #1)
        PositiveTestWithParameterForSI.instance().take_action()
        self.assertEqual(PositiveTestWithParameterForSI.instance().get_number(), 11)
        # Test if it is working. (case #n)
        PositiveTestWithParameterForSI.instance().take_action()
        self.assertEqual(PositiveTestWithParameterForSI.instance().get_number(), 12)
    
    def test_positive_using_decorator_with_parameter_for_dependency_injection(self):
        ''' Test if the target class without a singleton attribute but using a decorator with DI-compatible instance-reference parameter. '''
        try:
            class SampleDependencyInjection(object): pass
            sample_di = SampleDependencyInjection()
            @singleton(sample_di)
            class PositiveTestWithParameterForIRDI(TestSingletonClass.DummyTest):
                def __init__(self, dependency_injection):
                    super(self.__class__, self).__init__()
                    self.dependency_injection = dependency_injection
            self.assertTrue(True, 'Singleton Class: Passed the initialization as expected.')
        except SingletonInitializationException:
            self.assertTrue(False, 'Singleton Class: Failed the initialization with known exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
        # Test for the type.
        self.assertIsInstance(PositiveTestWithParameterForIRDI.instance(), PositiveTestWithParameterForIRDI)
        # Test if it is working. (case #1)
        PositiveTestWithParameterForIRDI.instance().take_action()
        self.assertEqual(PositiveTestWithParameterForIRDI.instance().get_number(), 1)
        # Test if it is working. (case #n)
        PositiveTestWithParameterForIRDI.instance().take_action()
        self.assertEqual(PositiveTestWithParameterForIRDI.instance().get_number(), 2)
        # Test if the dependency injection is working.
        self.assertIsInstance(PositiveTestWithParameterForIRDI.instance().dependency_injection, SampleDependencyInjection)
    
    def test_positive_using_decorator_with_parameter_for_dependency_injection_with_class_reference(self):
        ''' Test if the target class without a singleton attribute but using a decorator with DI-compatible class-reference parameter. '''
        try:
            class SampleDependencyInjection(object): pass
            @singleton(SampleDependencyInjection)
            class PositiveTestWithParameterForCRDI(TestSingletonClass.DummyTest):
                def __init__(self, dependency_injection):
                    super(self.__class__, self).__init__()
                    self.dependency_injection = dependency_injection
            self.assertTrue(True, 'Singleton Class: Passed the initialization as expected.')
        except SingletonInitializationException:
            self.assertTrue(False, 'Singleton Class: Failed the initialization with known exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
        # Test for the type.
        self.assertIsInstance(PositiveTestWithParameterForCRDI.instance(), PositiveTestWithParameterForDI)
        # Test if it is working. (case #1)
        PositiveTestWithParameterForCRDI.instance().take_action()
        self.assertEqual(PositiveTestWithParameterForCRDI.instance().get_number(), 1)
        # Test if it is working. (case #n)
        PositiveTestWithParameterForCRDI.instance().take_action()
        self.assertEqual(PositiveTestWithParameterForCRDI.instance().get_number(), 2)
        # Test if the dependency injection is working.
        self.assertTrue(PositiveTestWithParameterForCRDI.instance().dependency_injection is SampleDependencyInjection)
    
    def test_negative_with_existed_singleton_instance(self):
        ''' Test if the target class is with null singleton attribute. '''
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
            self.assertTrue(True, 'Singleton Class: Failed the initialization unexpectedly.')
    
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
            self.assertTrue(True, 'Singleton Class: Failed the initialization unexpectedly.')

# import sys
# @singleton
# class A(object): pass
# sys.exit()

if __name__ == '__main__':
    unittest.main()