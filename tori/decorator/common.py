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

def singleton_with(*args, **kwargs):
    '''
    Decorator to make a class to be a singleton class with given parameters
    for the constructor.
    
    Please note that this decorator always requires parameters. Not giving one
    may result errors. Additionally, it is designed to solve the problem where
    the first parameter is a class reference. For normal usage, please use
    `@singleton` instead.
    
    Example:
    
    .. code-block:: python
        # Declaration
        class MyAdapter(AdapterClass):
            def broadcast(self):
                print "Hello, world."
        @singleton_with(MyAdapter)
        class MyClass(ParentClass):
            def __init__(self, adapter):
                self.adapter = adapter()
            def take_action(self):
                self.adapter.broadcast()

        # Executing
        MyClass.instance().take_action() # expecting the message on the console.

    The end result is that the console will show the number from 1 to 10.
    '''
    # Only use the closure to handle the instatiation of the singleton of the instance.
    def inner_decorator(class_reference):
        return __make_a_singleton_class(class_reference, *args, **kwargs)
    return inner_decorator
    
    
def singleton(*args, **kwargs):
    '''
    Decorator to make a class to be a singleton class. This decorator is
    designed to be able to take parameters for the construction of the
    singleton instance.
    
    Please note that this decorator doesn't support the first parameter
    as a class reference. If you are using that way, please try to use
    `@singleton_with` instead.

    Example:
    
    .. code-block:: python
        # Declaration
        @singleton
        class MyFirstClass(ParentClass):
            def __init__(self):
                self.number = 0
            def call(self):
                self.number += 1
                echo self.number
        # Or
        @singleton(20)
        class MySecondClass(ParentClass):
            def __init__(self, init_number):
                self.number = init_number
            def call(self):
                self.number += 1
                echo self.number
        
        # Executing
        for i in range(10):
            MyFirstClass.instance().call()
        # Expecting 1-10 to be printed on the console.
        for i in range(10):
            MySecondClass.instance().call()
        # Expecting 11-20 to be printed on the console.
        

    The end result is that the console will show the number from 1 to 10.
    '''
    # Get the first parameter.
    first_param = args[0]    
    # If the first parameter is really a reference to a class, then instantiate
    # the singleton instance.
    if len(args) == 1 and inspect.isclass(first_param) and isinstance(first_param, type):
        class_reference = first_param
        return __make_a_singleton_class(class_reference)
    # Otherwise, use the closure to handle the parameter.
    def inner_decorator(class_reference):
        return __make_a_singleton_class(class_reference, *args, **kwargs)
    return inner_decorator
    