# -*- coding: utf-8 -*-

"""
:Author: Juti Noppornpitak
:Restriction: Internal Use Only

This package contains the rendering service. This is a module automatically loaded by :class:`tori.application.Application`.
"""

from tori.exception           import *
from tori.template.renderer   import Renderer
from tori.template.repository import Repository

class RenderingService(object):
    """
    The rendering service allows the access to all template repositories.

    :param renderer_class: a class reference of a renderer
    :type renderer_class: tori.template.renderer.Renderer
    :param repository_class: a class reference of a template repository
    :type repository_class: tori.template.repository.Repository
    """

    def __init__(self, renderer_class=Renderer, repository_class=Repository):
        self._repository = repository_class(renderer_class)

    def register(self, renderer):
        """
        Register a renderer.

        :param renderer: the renderer
        :type renderer: tori.template.renderer.Renderer
        :return: ``self``.
        """
        self._repository.set(renderer)

        return self

    def render(self, repository_name, template_path, **contexts):
        """
        Render a template from a repository *repository_name*.

        As this method acts as a wrapper to the actual renderer for the given repository,
        see :meth:`tori.template.renderer.Renderer.render` for more information.

        :rtype: string
        """
        return self._repository.get(repository_name).render(template_path, **contexts)
