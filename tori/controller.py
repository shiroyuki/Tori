from os             import path as p
from mimetypes      import guess_type as get_type
from re             import match, sub
from StringIO       import StringIO

from tornado        import web
from tori.renderer  import DefaultRenderer, RendererService
from tori.exception import *

class Controller(web.RequestHandler):
    def render(self, template_name, **contexts):
        if not self._rendering_source:
            raise RenderingSourceMissingError, 'The source of template is not identified. This method is disabled.'
        
        if not self._rendering_engine:
            self._rendering_engine = DefaultRenderer
        
        output = None
        try:
            output = RendererService.instance().render(
                self._rendering_source,
                template_name,
                **contexts
            )
        except RendererNotFoundError:
            # When the renderer is not found. It is possible that the renderer is not yet
            # instantiated. This block of the code will do the lazy loading.
            renderer = self._rendering_engine(self._rendering_source)
            RendererService.instance().register(renderer).render(
                self._rendering_source,
                template_name,
                **contexts
            )
        
        self.write(output)

class ResourceEntity(object):
    def __init__(self, path):
        self.path     = path
        self._content = None
        
        self.type     = get_type(path)
        self.type     = self.type[0]
    
    def content(self):
        if self._content:
            return self._content
        
        if not p.exists(self.path):
            return None
        
        with open(self.path) as f:
            self._content = f.read()
        
        return self._content

class ResourceService(web.RequestHandler):
    _patterns        = {}
    _cached_patterns = []
    _cache_objects   = {}
    
    @staticmethod
    def add_pattern(pattern, base_path, enabled_cache=False):
        ResourceService._patterns[pattern] = base_path
    
    def get(self, path):
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