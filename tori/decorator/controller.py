"""
:Author: Juti Noppornpitak

This package contains decorators for enhancing controllers.
"""
try:
    # Python 2.6+
    import httplib
except ImportError as error:
    # Python 3.3+
    import http.client as httplib

import traceback

from tori.exception import *

def _assign_renderer(class_reference, base_path, engine=None):
    """
    Assign the renderer to the given controller-type class.

    `class_reference` is a reference to a class type, not an instance of a class.

    The first argument called `source` is a name of the package containing templates and static contents.

    The second argument called `renderer_type` is a name of a renderer-type class used to override the default renderer.

    To use this, suppose we have a class called `DummyController` and later instantiate
    a variable `dummy_controller` as an instance of class `DummyController`. `class_reference`
    will be `DummyController`, not `dummy_controller`.

    Note that this method is not for direct use. You can invoke via `@renderer` or the
    configuration file only via `tori.application.Application`.

    Additionally, the arguments might be different if the renderer is not the default one.
    """
    class_reference._template_base_path = base_path
    class_reference._template_engine    = engine

    return class_reference

def renderer(*args, **kwargs):
    """ Set up the renderer for a controller.

    See :class:`tori.template.renderer.Renderer` for more information.
    """
    def inner_decorator(class_reference):
        if len(args) == 0:
            raise InvalidInput

        return _assign_renderer(class_reference, *args, **kwargs)

    return inner_decorator

def _enable_custom_error(controller, template_name, **contexts):
    def write_error(self, status_code, **kwargs):
        debug_info = []

        if self.settings.get("debug") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            for line in traceback.format_exception(*kwargs["exc_info"]):
                debug_info.append(line)

        self.render(
            template_name,
            code       = status_code,
            message    = httplib.responses[status_code],
            debug_info = ''.join(debug_info),
            **contexts
        )

    controller.write_error = write_error

def custom_error(template_name, **contexts):
    """ Set up the controller to handle exceptions with a custom error page.

    .. note:: This decorator is to override the method ``write_error``.

    :param template_name: the name of the template to render.
    :type  template_name: string
    :param contexts:      map of context variables
    :type  contexts:      dict
    """
    def updated_controller(controller):
        _enable_custom_error(controller, template_name, **contexts)

        return controller

    return updated_controller