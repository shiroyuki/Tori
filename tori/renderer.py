from   os import path
import re

from   jinja2 import Environment, FileSystemLoader, PackageLoader

from   tori.decorator.common import singleton
from   tori.exception        import *
from   tori.template         import TemplateRepository

class Renderer(object):
    def __init__(self, template_module_name):
        raise FutureFeatureException, "Need to implement."
    
    def render(self, template_path, **contexts):
        raise FutureFeatureException, "Need to implement."

class DefaultRenderer(Renderer):
    def __init__(self, *referers):
        '''
        The default renderer with Jinja2
        
        `referers` is either the name of the resource module or multiple path to templates (based on the current working directory).
        '''
        
        if len(referers) == 0:
            raise RendererSetupError, 'Require either one resource module or multiple file paths to the templates.'
        
        self.name     = ':'.join(referers)
        self.referers = referers
        
        self.loader   = (len(self.referers) == 1 and not path.exists(self.referers[0])) \
            and self.__get_package_loader() \
            or  self.__get_filesystem_loader()
        self.storage  = Environment(loader=self.loader)
    
    def __get_filesystem_loader(self):
        for location in self.referers:
            if not path.exists(location):
                raise RendererSetupError, '%s is not found on this system.' % location
        
        return FileSystemLoader(self.referers)
    
    def __get_package_loader(self):
        module_name_chunks       = re.split('\.', self.name)
        module_name              = '.'.join(module_name_chunks[:-1])
        template_sub_module_name = module_name_chunks[-1]
        
        if len(module_name_chunks) <= 1:
            raise RendererSetupError, 'Could not instantiate the package loader.'
        
        return PackageLoader(module_name, template_sub_module_name)
    
    def render(self, template_path, **contexts):
        template = self.storage.get_template(template_path)
        
        return template.render(**contexts)

@singleton
class RenderingService(object):
    def __init__(self, renderer_class=Renderer, repository_class=TemplateRepository):
        self._repository = repository_class(renderer_class)
    
    def register(self, renderer):
        self._repository.set(renderer)
        
        return self
    
    def render(self, renderer_name, template_path, **contexts):
        return self._repository.get(renderer_name).render(template_path, **contexts)
        