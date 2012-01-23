from tornado import web

def disable_access(action):
    '''
    Disable access to the targeted action of the controller.
    '''
    def __override_action__(*args, **kwargs):
        raise web.HTTPError(403)
    return __override_action__

def renderer(source, renderer_type=None):
    def inner_decorator(class_reference):
        class_reference._rendering_source = source
        class_reference._rendering_engine = renderer_type
        return class_reference
    return inner_decorator
