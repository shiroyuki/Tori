from tornado import web

def disable_access(action):
    '''
    Disable access to the targeted action of the controller.
    '''
    def __override_action__(*args, **kwargs):
        raise web.HTTPError(403)
    return __override_action__

def _assign_renderer(class_reference, source, renderer_type=None):
    '''
    Assign the renderer to the given controller-type class.
    
    `class_reference` is a reference to a class type, not an instance of a class.
    
    `source` is a name of the package containing templates and static contents.
    
    `renderer_type` is a name of a renderer-type class used to override the default renderer.
    
    To use this, suppose we have a class called `DummyController` and later instantiate
    a variable `dummy_controller` as an instance of class `DummyController`. `class_reference`
    will be `DummyController`, not `dummy_controller`.
    
    Note that this method is not for direct use. You can invoke via `@renderer` or the
    configuration file only via `tori.application.DIApplication`.
    '''
    class_reference._rendering_source = source
    class_reference._rendering_engine = renderer_type
    
    return class_reference

def renderer(source, renderer_type=None):
    def inner_decorator(class_reference):
        return _assign_renderer(class_reference, source, renderer_type)
    
    return inner_decorator
