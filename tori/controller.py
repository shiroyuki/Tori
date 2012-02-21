'''
:Author: Juti Noppornpitak

This package contains an abstract controller (based on :class:`tornado.web.RequestHandler`) and built-in controllers.
'''

from os             import path as p
from mimetypes      import guess_type as get_type
from re             import match, sub
from StringIO       import StringIO

from tornado        import web
from tori.renderer  import DefaultRenderer, RenderingService
from tori.exception import *

class Controller(web.RequestHandler):
    '''
    The abstract controller for Tori framework which replaces Jinja2 as a template engine instead.
    '''
    # def write_error(status_code, **kwargs):
    #         if status_code == 500:
    #             self.write('Server Error')
    #         self.write('What the fuck')
    #         self.flush()
    #
    
    def render(self, template_name, **contexts):
        '''
        Render the template with the given contexts.
        
        See :meth:`Renderer.render` for more information.
        '''
        
        if not self._rendering_source:
            raise RenderingSourceMissingError, 'The source of template is not identified. This method is disabled.'
        
        if not self._rendering_engine:
            self._rendering_engine = DefaultRenderer
        
        output = None
        
        try:
            output = RenderingService.instance().render(
                self._rendering_source,
                template_name,
                **contexts
            )
        except RendererNotFoundError:
            # When the renderer is not found. It is possible that the renderer is not yet
            # instantiated. This block of the code will do the lazy loading.
            renderer = self._rendering_engine(self._rendering_source)
            output   = RenderingService.instance().register(renderer).render(
                self._rendering_source,
                template_name,
                **contexts
            )
        
        if not output:
            raise UnexpectedComputationError, 'Detected the rendering service malfunctioning.'
        
        self.write(output)

class ResourceEntity(object):
    '''
    Static resource entity representing the real static resource which is already loaded to the memory.
    
    *path* is the path to the static resource.
    
    .. note::
        This is for internal use only.
    '''
    def __init__(self, path):
        self.path     = path
        self._content = None
        
        self.type     = get_type(path)
        self.type     = self.type[0]
    
    def content(self):
        ''' Get the content of the entity. '''
        if self._content:
            return self._content
        
        if not p.exists(self.path):
            return None
        
        with open(self.path) as f:
            self._content = f.read()
        
        return self._content

class ResourceService(web.RequestHandler):
    ''' Resource service is to serve a static resource via HTTP/S protocal. '''
    
    _patterns        = {}
    _cached_patterns = []
    _cache_objects   = {}
    
    @staticmethod
    def add_pattern(pattern, base_path, enabled_cache=False):
        '''
        Add the routing pattern for the resource path prefix.
        
        *pattern* is a routing pattern. It is a Python-compatible regular expression.
        
        *base_path* is a path prefix of the resource corresponding to the routing pattern.
        
        *enabled_cache* is a flag to indicate whether any loaded resources need to be cached on the first request.
        '''
        ResourceService._patterns[pattern] = base_path
    
    def get(self, path):
        '''
        Get a particular resource.
        
        .. note::
            This method requires refactoring.
        '''
        
        base_path    = None
        real_path    = None
        resource     = None
        used_pattern = None
        request_uri  = self.request.uri
        has_cache    = ResourceService._cache_objects.has_key(request_uri)
        
        # Remove the prefixed foreslashes.
        path = sub('^/+', '', path)
        
        if has_cache:
            resource = ResourceService._cache_objects[request_uri]
        elif ResourceService._patterns.has_key(request_uri):
            used_pattern = request_uri
            real_path    = ResourceService._patterns[request_uri]
        else:
            for pattern in ResourceService._patterns:
                if not match(pattern, request_uri):
                    continue
                
                used_pattern = pattern
                real_path    = p.abspath(p.join(
                    ResourceService._patterns[pattern],
                    path
                ))
                
                break
        
        if not resource:
            resource = ResourceEntity(real_path)
        
        if not has_cache and used_pattern in ResourceService._cached_patterns:
            ResourceService._cached_patterns[used_pattern] = resource
        
        resource_type = resource.type or 'text/plain'
        
        self.set_header("Content-Type", resource_type)
        
        try:
            self.write(resource.content())
        except Exception, e:
            print 'Failed on resource distribution.'
            print e, type(e)