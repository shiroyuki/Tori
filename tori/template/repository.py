# -*- coding: utf-8 -*-

"""
:Author: Juti Noppornpitaks
:Restriction: Internal Use Only
"""

from tori.exception import *

class Repository(dict):
    """
    The template repository used by Rendering Service.

    :param class_reference: class reference
    :type class_reference:  tori.template.service.RenderingService

    .. note::
        This class is designed as a strict-type collection and may be refactored
        to the common area later on.
    """
    def __init__(self, class_reference):
        self._class_reference = class_reference

    def get(self, renderer_name):
        """
        Retrieve the renderer by name.

        :param renderer_name: the name of the renderer.
        :type renderer_name: string or unicode
        :rtype: tori.template.renderer.Renderer
        """
        if renderer_name not in self:
            raise RendererNotFoundError

        return self[renderer_name]

    def set(self, renderer):
        """
        Register the renderer.

        :return: self
        """
        if not isinstance(renderer, self._class_reference):
            raise UnsupportedRendererError('Expected an instance of %s but received %s.' % (self._class_reference, type(renderer)))

        self[renderer.name] = renderer

        return self
