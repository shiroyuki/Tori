'''
:Author: Juti Noppornpitak

This package contains decorators for enhancing controllers.
'''
from tori.exception import *

def disable_access(action):
    '''
    Disable access to the targeted action of the controller.
    '''
    def __override_action__(*args, **kwargs):
        raise web.HTTPError(403)
    
    return __override_action__

def _assign_renderer(class_reference, *args, **kwargs):
    '''
    Assign the renderer to the given controller-type class.
    
    `class_reference` is a reference to a class type, not an instance of a class.
    
    The first argument called `source` is a name of the package containing templates and static contents.
    
    The second argument called `renderer_type` is a name of a renderer-type class used to override the default renderer.
    
    To use this, suppose we have a class called `DummyController` and later instantiate
    a variable `dummy_controller` as an instance of class `DummyController`. `class_reference`
    will be `DummyController`, not `dummy_controller`.
    
    Note that this method is not for direct use. You can invoke via `@renderer` or the
    configuration file only via `tori.application.DIApplication`.
    
    Additionally, the arguments might be different if the renderer is not the default one.
    '''
    class_reference._rendering_source = args[0]
    class_reference._rendering_engine = len(args) > 1 and args[1] or None
    
    return class_reference

def renderer(*args, **kwargs):
    '''
    Set up the renderer of a controller (``class_reference``).
    
    See :class:`tori.renderer.Renderer` for more information.
    '''
    def inner_decorator(class_reference):
        if len(args) == 0:
            raise InvalidInput
        
        return _assign_renderer(class_reference, *args, **kwargs)
    
    return inner_decorator
