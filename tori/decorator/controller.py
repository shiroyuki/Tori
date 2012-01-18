import tornado.web.HTTPError

def disable_access(action):
    '''
    Disable access to the targeted action of the controller.
    '''
    def __override_action__(*args, **kwargs):
        raise tornado.web.HTTPError(403)
    return __override_action__
