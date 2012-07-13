# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitaks
:Purpose: Internal Use Only

The template repository used by Rendering Service (:class:`tori.renderer.RenderingService`).
'''

from tori.exception import *

class TemplateRepository(dict):
    def __init__(self, class_reference):
        self._class_reference = class_reference

    def get(self, module_name):
        if not self.has_key(module_name):
            raise RendererNotFoundError

        return self[module_name]

    def set(self, renderer):
        if not isinstance(renderer, self._class_reference):
            raise UnsupportedRendererError, 'Expected an instance of %s but received %s.' % (self._class_reference, type(renderer))

        self[renderer.name] = renderer

        return self
