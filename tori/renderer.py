'''
:Author: Juti Noppornpitaks

This package is used for rendering.
'''

from   os import path
import re

from   jinja2 import Environment, FileSystemLoader, PackageLoader

from   tori.decorator.common import singleton
from   tori.exception        import *
from   tori.template         import TemplateRepository

class Renderer(object):
    '''
    The abstract renderer for Tori framework.
    
    .. warning::
        This is not a working renderer. To use the built-in renderer (using Jinja2), try :class:`DefaultRenderer`.
        Otherwise, you should be expecting :class:`tori.exception.FutureFeatureException`.
    '''
    def __init__(self, *args, **kwargs):
        raise FutureFeatureException, "Need to implement."
    
    def render(self, template_path, **contexts):
        '''
        Render a template with context variables.
        
        *contexts* is a dictionary of context variables.
        
        Example::
        
            renderer = Renderer()
            renderer.render('dummy.html', appname='ikayaki', version=1.0)
        
        '''
        raise FutureFeatureException, "Need to implement."

class DefaultRenderer(Renderer):
    '''
    The default renderer with Jinja2
        
    `referers` is either the template module path or multiple base paths of Jinja templates (based on the current
    working directory).
    
    For example::
    
        # Instantiate with the module path.
        renderer = DefaultRenderer('app.views')
        # Instantiate with multiple base paths of Jinja templates.
        renderer = DefaultRenderer('/opt/app/ui/template', '/usr/local/tori/module/template')
    
    '''
    
    def __init__(self, *referers):
        if len(referers) == 0:
            raise RendererSetupError, 'Require either one resource module or multiple file paths to the templates.'
        
        self.name     = ':'.join(referers)
        self.referers = referers
        
        self.loader   = (len(self.referers) == 1 and not path.exists(self.referers[0])) \
            and self._get_package_loader() \
            or  self._get_filesystem_loader()
        self.storage  = Environment(loader=self.loader)
    
    def _get_filesystem_loader(self):
        '''
        Get the file-system loader for the renderer.
        
        .. warning::
            This is for internal use and only accessible for overriding purposes.
        '''
        for location in self.referers:
            if not path.exists(location):
                raise RendererSetupError, '%s is not found on this system.' % location
        
        return FileSystemLoader(self.referers)
    
    def _get_package_loader(self):
        '''
        Get the package loader for the renderer.
        
        .. warning::
            This is for internal use and only accessible for overriding purposes.
        '''
        
        module_name_chunks       = re.split('\.', self.name)
        module_name              = '.'.join(module_name_chunks[:-1])
        template_sub_module_name = module_name_chunks[-1]
        
        if len(module_name_chunks) <= 1:
            raise RendererSetupError, 'Could not instantiate the package loader.'
        
        return PackageLoader(module_name, template_sub_module_name)
    
    def render(self, template_path, **contexts):
        ''' See :meth:`Renderer.render` for more information. '''
        template = self.storage.get_template(template_path)
        
        return template.render(**contexts)

@singleton
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
        