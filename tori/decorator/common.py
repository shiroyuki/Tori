import inspect
import sys

class SingletonInitializationException(Exception):
    '''
    This exception is used when the target class contain a special
    attribute `_singleton_instance` not a reference to its own class.
    '''

def __make_a_singleton_class(class_reference, *args, **kwargs):
    # Name of the attribute that store the singleton instance
    singleton_attr_name = '_singleton_instance'
    # The statice method to get the singleton instance of the reference class
    @staticmethod
    def instance():
        ''' Get an instance. '''
        return class_reference._singleton_instance
    # Intercept if the class has already been a singleton class.
    if singleton_attr_name in dir(class_reference):
        raise SingletonInitializationException,\
            'The attribute _singleton_instance is already assigned as instance of %s.'\
            % type(class_reference._singleton_instance)
    # Instantiate an instance for a singleton class.
    class_reference._singleton_instance = class_reference(*args, **kwargs)
    class_reference.instance = instance
    return class_reference

def singleton(*args, **kwargs):
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
    # Get the first parameter.
    first_param = args[0]    
    # If the first parameter is really a reference to a class, then instantiate
    # the singleton instance.
    if inspect.isclass(first_param) and isinstance(first_param, type):
        class_reference = first_param
        return __make_a_singleton_class(class_reference)
    # Otherwise, use the closure to handle the parameter.
    def inner_decorator(class_reference):
        return __make_a_singleton_class(class_reference, *args, **kwargs)
    return inner_decorator
    