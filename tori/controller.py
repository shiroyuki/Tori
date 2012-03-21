'''
:Author: Juti Noppornpitak

This package contains an abstract controller (based on :class:`tornado.web.RequestHandler`) and built-in controllers.
'''

from os        import path as p
from mimetypes import guess_type as get_type
from re        import match, sub
from StringIO  import StringIO

from tornado.web            import HTTPError, ErrorHandler, RequestHandler
from tori                   import services as ToriService
from tori.renderer          import DefaultRenderer
from tori.exception         import *

class Controller(RequestHandler):
    '''
    The abstract controller for Tori framework which replaces Jinja2 as a template engine instead.
    '''
    
    def render_template(self, template_name, **contexts):
        '''
        Render the template with the given contexts.
        
        See :meth:`tori.renderer.Renderer.render` for more information.
        '''
        
        # If the rendering source isn't set, break the code.
        if not self._rendering_source:
            raise RenderingSourceMissingError, 'The source of template is not identified. This method is disabled.'
        
        # If the rendering engine is not specified, use the default one.
        if not self._rendering_engine:
            self._rendering_engine = DefaultRenderer
        
        output = None
        
        try:
            output = ToriService.get('renderer').render(
                self._rendering_source,
                template_name,
                **contexts
            )
        except RendererNotFoundError:
            # When the renderer is not found. It is possible that the renderer is not yet
            # instantiated. This block of the code will do the lazy loading.
            renderer = self._rendering_engine(self._rendering_source)
            output   = ToriService.get('renderer').register(renderer).render(
                self._rendering_source,
                template_name,
                **contexts
            )
        
        if not output:
            raise UnexpectedComputationError, 'Detected the rendering service malfunctioning.'
        
        return output
    
    def render(self, template_name, **contexts):
        '''
        Render the template with the given contexts.
        
        See :meth:`tori.renderer.Renderer.render` for more information.
        '''
        self.write(self.render_template(template_name, **contexts))

class ErrorController(Controller):
    """Generates an error response with status_code for all requests."""
    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        raise HTTPError(self._status_code)

class ResourceEntity(object):
    '''
    Static resource entity representing the real static resource which is already loaded to the memory.
    
    :param path: the path to the static resource.
    
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

class ResourceService(RequestHandler):
    ''' Resource service is to serve a static resource via HTTP/S protocal. '''
    
    _patterns = {}
    
    @staticmethod
    def add_pattern(pattern, base_path, enabled_cache=False):
        '''
        Add the routing pattern for the resource path prefix.
        
        :param pattern: a routing pattern. It can be a Python-compatible regular expression.
        
        :param base_path: a path prefix of the resource corresponding to the routing pattern.
        
        :param enabled_cache: a flag to indicate whether any loaded resources need to be cached on the first request.
        '''
        
        ResourceService._patterns[pattern] = base_path
    
    def get(self, *path):
        '''
        Get a particular resource.
        
        :param path: blocks of path used to composite an actual path.
        
        .. note::
            This method requires refactoring.
        '''
        base_path    = None
        resource     = None
        used_pattern = None
        request_uri  = self.request.uri
        
        # Remove the prefixed foreslashes.
        path = '/'.join(path)
        path = sub('^/+', '', path)
        
        if ResourceService._patterns.has_key(request_uri):
            # If the request URI is already pre-calculated or fixed, load the entity from the corresponding path.
            resource = self._get_resource_entity(ResourceService._patterns[request_uri])
        
        # When the resource is not loaded, try to get from the wildcard pattern.
        if not resource:
            resource = self._get_resource_on_non_precalculated_pattern(path)
        
        resource_type = resource.type or 'text/plain'
        
        self.set_header("Content-Type", resource_type)
        
        if not resource.content():
            raise HTTPError, 404
        
        try:
            self.finish(resource.content())
        except Exception, e:
            print 'Failed on resource distribution.'
            print e, type(e)
    
    def _get_resource_entity(self, real_path):
        return ResourceEntity(real_path)
    
    def _get_resource_on_non_precalculated_pattern(self, path_to_resource):
        request_uri = self.request.uri
        
        for pattern in ResourceService._patterns:
            if not match(pattern, request_uri):
                continue
                
            used_pattern = pattern
            real_path    = p.abspath(p.join(
                ResourceService._patterns[pattern],
                path_to_resource
            ))
            
            return self._get_resource_entity(real_path)
        
        raise HTTPError(404)