import unittest

class SingletonInitializationException(Exception):
    '''
    This exception is used when the target class contain a special
    attribute `_singleton_instance` not a reference to its own class.
    '''

def singleton(class_reference):
    '''
    Decorator to make a class to be a singleton class.

    Example:
    
    .. code-block:: python
        # Declaration
        @singleton
        class MyClass(ParentClass):
            def __init__(self):
                self.number = 0
            def call(self):
                self.number += 1
                echo self.number

        # Executing
        for i in range(10):
            MyClass.instance().call()

    The end result is that the console will show the number from 1 to 10.
    '''
    # Name of the attribute that store the singleton instance
    singleton_attr_name = '_singleton_instance'
    # The statice method to get the singleton instance of the reference class
    @staticmethod
    def instance():
        ''' Get an instance. '''
        return class_reference._singleton_instance
    # Instantiate an instance for a singleton class.
    if singleton_attr_name in dir(class_reference):
        raise SingletonInitializationException,\
            'The attribute _singleton_instance is already assigned as instance of %s.'\
            % type(class_reference._singleton_instance)
    else:
        class_reference._singleton_instance = class_reference()
        class_reference.instance = instance
    return class_reference

class TestSingletonClass(unittest.TestCase):
    class DummyTest(object):
        def __init__(self):
            self.__number = 0
        def take_action(self):
            self.__number += 1
        def get_number(self):
            return self.__number
    def test_positive_without_instance_attr(self):
        try:
            @singleton
            class PositiveTestWithoutInstanceAttr(TestSingletonClass.DummyTest): pass
            self.assertTrue(True, 'Singleton Class: Passed the initialization as expected.')
        except SingletonInitializationException:
            self.assertTrue(False, 'Singleton Class: Failed the initialization with known exception.')
        except:
            self.assertTrue(False, 'Singleton Class: Failed the initialization unexpectedly.')
        self.assertIsInstance(PositiveTestWithoutInstanceAttr.instance(), PositiveTestWithoutInstanceAttr)
        PositiveTestWithoutInstanceAttr.instance().take_action()
        self.assertEqual(PositiveTestWithoutInstanceAttr.instance().get_number(), 1)
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
            

if __name__ == '__main__':
    unittest.main()