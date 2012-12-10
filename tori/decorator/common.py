"""
:Author: Juti Noppornpitak

This package contains decorators for common use.
"""

import inspect
from   tori.exception import *

class BaseDecoratorForCallableObject(object):
    """
    Base decorator based from an example at http://www.artima.com/weblogs/viewpost.jsp?thread=240808.
    """
    def __init__(self, reference):
        """ On the initialization of the given ``function``. """
        self._reference = reference

    def reference(self):
        return self._reference

    def __call__(self, *args, **kwargs):
        """ On the execution of the function. """
        pass

def make_singleton_class(class_reference, *args, **kwargs):
    """
    Make the given class a singleton class.

    *class_reference* is a reference to a class type, not an instance of a class.

    *args* and *kwargs* are parameters used to instantiate a singleton instance.

    To use this, suppose we have a class called ``DummyClass`` and later instantiate
    a variable ``dummy_instnace`` as an instance of class ``DummyClass``. ``class_reference``
    will be ``DummyClass``, not ``dummy_instance``.

    Note that this method is not for direct use. Always use ``@singleton`` or ``@singleton_with``.
    """
    # Name of the attribute that store the singleton instance
    singleton_attr_name = '_singleton_instance'

    # The statice method to get the singleton instance of the reference class
    @staticmethod
    def instance():
        """
        Get a singleton instance.

        .. note:: This class is capable to act as a singleton class by invoking this method.
        """
        return class_reference._singleton_instance

    # Intercept if the class has already been a singleton class.
    if singleton_attr_name in dir(class_reference):
        raise SingletonInitializationException(
            'The attribute _singleton_instance is already assigned as instance of %s.'\
            % type(class_reference._singleton_instance)
        )

    # Instantiate an instance for a singleton class.
    class_reference._singleton_instance = class_reference(*args, **kwargs)
    class_reference.instance            = instance

    return class_reference

def singleton_with(*args, **kwargs):
    """
    Decorator to make a class to be a singleton class with given parameters
    for the constructor.

    Please note that this decorator always requires parameters. Not giving one
    may result errors. Additionally, it is designed to solve the problem where
    the first parameter is a class reference. For normal usage, please use
    `@singleton` instead.

    Example::

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
    """
    # Only use the closure to handle the instatiation of the singleton of the instance.
    def inner_decorator(class_reference):
        return make_singleton_class(class_reference, *args, **kwargs)

    return inner_decorator


def singleton(*args, **kwargs):
    """
    Decorator to make a class to be a singleton class. This decorator is
    designed to be able to take parameters for the construction of the
    singleton instance.

    Please note that this decorator doesn't support the first parameter
    as a class reference. If you are using that way, please try to use
    ``@singleton_with`` instead.

    Example::

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
    """
    # Get the first parameter.
    first_param = args[0]

    # If the first parameter is really a reference to a class, then instantiate
    # the singleton instance.
    if len(args) == 1 and inspect.isclass(first_param) and isinstance(first_param, type):
        class_reference = first_param

        return make_singleton_class(class_reference)

    # Otherwise, use the closure to handle the parameter.
    def inner_decorator(class_reference):
        return make_singleton_class(class_reference, *args, **kwargs)

    return inner_decorator
