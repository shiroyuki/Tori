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
    # The flag to see if the instance is initialized.
    is_instance_initialised = False;
    # Static method
    @staticmethod
    def instance():
        return class_reference._instance
    try:
        if not class_reference._instance:
            class_reference._instance = class_reference()
            is_instance_initialised = True
    except AttributeError:
        class_reference._instance = class_reference()
        is_instance_initialised = True
    if is_instance_initialised:
        class_reference.instance = instance
    return class_reference
