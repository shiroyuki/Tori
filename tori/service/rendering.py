'''
:Author: Juti Noppornpitak

This package contains the rendering service. This is a module automatically loaded by :class:`tori.application.Application`.
'''

from tori.decorator.common import singleton
from tori.exception        import *
from tori.renderer         import Renderer
from tori.template         import TemplateRepository

class RenderingService(object):
    '''
    The rendering service allows the access to all template repositories.
    
    *renderer_class* is a class reference for a renderer.
    
    *repository_class* is a class reference for a template repository.
    
    .. note::
        This should be moved to ``tori.service``.
    '''
    
    def __init__(self, renderer_class=Renderer, repository_class=TemplateRepository):
        self._repository = repository_class(renderer_class)
    
    def register(self, renderer):
        ''' Register a *renderer* which is an instance of :class:`Renderer`. '''
        self._repository.set(renderer)
        
        return self
    
    def render(self, repository_name, template_path, **contexts):
        '''
        Render a template from a repository *repository_name*.
        
        As this method acts as a wrapper to the actual renderer for the given repository,
        see :meth:`Renderer.render` for more information.
        '''
        return self._repository.get(repository_name).render(template_path, **contexts)
