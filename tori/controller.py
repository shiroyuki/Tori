'''
:Author: Juti Noppornpitak

This package contains an abstract controller (based on :class:`tornado.web.RequestHandler`) and built-in controllers.
'''

from os        import path as p
from mimetypes import guess_type as get_type
from re        import match, sub
from StringIO  import StringIO
from time      import time

from tornado.web import HTTPError, ErrorHandler, RequestHandler

from tori           import __version__
from tori.centre    import services as ToriService
from tori.common    import Enigma, Console
from tori.exception import *
from tori.renderer  import DefaultRenderer
from tori.service.data.base import ResourceEntity

class Controller(RequestHandler):
    '''
    The abstract controller for Tori framework which replaces Jinja2 as a template engine instead.
    '''
    
    def __init__(self, *args, **kwargs):
        RequestHandler.__init__(self, *args, **kwargs)
        
        self.session_id   = None
        self.session_repo = None
        
        # Start the session if the session component is registered.
        self._start_session()
    
    def _start_session(self):
        ''' Start the session. '''
        if not ToriService.has('session') or 'cookie_secret' not in self.settings:
            return
        
        self.session_repo = ToriService.get('session')
        self.session_id   = self.get_secure_cookie('ssid')
        
        if not self.session_id:
            self.session_id = self.session_repo.generate()
            
            self.set_secure_cookie('ssid', self.session_id)
    
    def component(self, name):
        '''
        Get the (re-usable) component from the initialized Imagination component locator service.
        
        :param `name`: the name of the registered re-usable component.
        :return:       module, package registered or ``None``
        '''
        return ToriService.has(name) and ToriService.get(name) or None
    
    def session(self, key, new_content=None):
        '''
        Get the session or set it if ``new_content`` is set.
        
        :param `key`:         Session data key
        :param `new_content`: Session data content
        
        :return: the data stored in the session or ``None``
        '''
        if not self.session_repo:
            raise SessionError, 'This session component is not initialized.'
        
        if new_content:
            self.session_repo.set(self.session_id, key, new_content)
            return new_content
        
        session = self.session_repo.get(self.session_id, key)
        
        return session
    
    def delete_session(self, key):
        self.component('session').delete(self.session_id, key)
    
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
            output = self.component('renderer').render(
                self._rendering_source,
                template_name,
                **contexts
            )
        except RendererNotFoundError:
            # When the renderer is not found. It is possible that the renderer is not yet
            # instantiated. This block of the code will do the lazy loading.
            renderer = self._rendering_engine(self._rendering_source)
            output   = self.component('renderer').register(renderer).render(
                self._rendering_source,
                template_name,
                **contexts
            )
        
        if not output:
            raise UnexpectedComputationError, 'Detected the rendering service malfunctioning.'
        
        return output
    
    def render(self, template_name, **contexts):
        '''
        Render the template with the given contexts and push the output buffer.
        
        See :meth:`tori.renderer.Renderer.render` for more information.
        '''
        self.write(self.render_template(template_name, **contexts))

class RestController(Controller):
    '''
    Abstract REST-capable controller based on a single primary key.
    '''
    def list(self):
        ''' Retrieve the list of all entities. '''
        self.set_status(405)
    
    def retrieve(self, id):
        ''' Retrieve an entity with `id`. '''
        self.set_status(405)
    
    def create(self):
        ''' Create an entity. '''
        self.set_status(405)
    
    def remove(self, id):
        ''' Remove an entity with `id`. '''
        self.set_status(405)

    def update(self, id):
        ''' Update an entity with `id`. '''
        self.set_status(405)
    
    def get(self, id=None):
        ''' Handle GET requests. '''
        if not id:
            self.list()
            return
        
        self.retrieve(int(id))
    
    def post(self, id=None):
        ''' Handle POST requests. '''
        if id:
            self.set_status(405)
            return
        
        self.create()
    
    def put(self, id=None):
        ''' Handle PUT requests. '''
        if not id:
            self.set_status(405)
            return
        
        self.update(int(id))
    
    def delete(self, id=None):
        ''' Handle DELETE requests. '''
        if id:
            self.set_status(405)
            return
        
        self.remove(int(id))

class ErrorController(Controller):
    """Generates an error response with status_code for all requests."""
    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        raise HTTPError(self._status_code)

class ResourceService(RequestHandler):
    ''' Resource service is to serve a static resource via HTTP/S protocal. '''
    
    _patterns      = {}
    _cache_objects = {}
    
    _plugins            = {}
    _plugins_tag_name   = 'resource-service-plugin'
    _plugins_registered = False
    
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
        
        # If the request URI is already pre-calculated or fixed, load the
        # entity from the corresponding path.
        if ResourceService._patterns.has_key(request_uri):
            resource = self._get_resource_entity(ResourceService._patterns[request_uri])
        
        # When the resource is not loaded, try to get from the wildcard pattern.
        if not resource:
            resource = self._get_resource_on_non_precalculated_pattern(path)
        
        # Get the resource type.
        resource_type = resource.type or 'text/plain'
        
        self.set_header("Content-Type", resource_type)
        
        # Return HTTP 404 if the content is not found.
        if not resource.content():
            raise HTTPError, 404
        
        # Retrieve the plugins if registered.
        if not ResourceService._plugins_registered:
            ResourceService._plugins = ToriService.getListByTag(
                ResourceService._plugins_tag_name
            )
        
        # Apply the plugin.
        for plugin in ResourceService._plugins:
            if plugin.expect(resource):
                resource = plugin.execute(resource)
            # End the iteraltion
        
        # Return the content.
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
        
        raise HTTPError, 404