1# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitak

This package contains an abstract controller (based on
:class:`tornado.web.RequestHandler`) and built-in controllers.
'''

import logging
from os        import path as p
from mimetypes import guess_type as get_type
from re        import match, search, sub
from StringIO  import StringIO
from time      import time

from tornado.web import HTTPError, ErrorHandler, RequestHandler

from tori           import __version__
from tori.centre    import services as ComponentRepository
from tori.common    import Enigma, getLogger
from tori.exception import *
from tori.template.renderer import DefaultRenderer
from tori.data.base import ResourceEntity

class Controller(RequestHandler):
    '''
    The abstract controller for Tori framework which uses Jinja2 as a template
    engine instead of the default one that comes with Tornado.
    '''

    def __init__(self, *args, **kwargs):
        RequestHandler.__init__(self, *args, **kwargs)

        self.session_id   = None
        self.session_repo = None

        # Start the session if the session component is registered.
        self.start_session()

    def start_session(self):
        ''' Start the session. '''
        if not ComponentRepository.has('session'):
            return

        self.session_repo = ComponentRepository.get('session')
        self.session_id   = self._can_use_secure_cookie()\
            and self.get_secure_cookie('ssid')\
            or self.get_cookie('ssid')

        if self.session_id:
            return

        self.session_id = self.session_repo.generate()

        if self._can_use_secure_cookie():
            self.set_secure_cookie('ssid', self.session_id)
        else:
            self.set_cookie('ssid', self.session_id)
        # endif

    def _can_use_secure_cookie(self):
        return 'cookie_secret' in self.settings\
            and self.settings['cookie_secret']

    def component(self, name, fork_component=False):
        '''
        Get the (re-usable) component from the initialized Imagination
        component locator service.

        :param `name`:           the name of the registered re-usable component.
        :param `fork_component`: the flag to fork the component
        :return:                 module, package registered or ``None``
        '''

        if not ComponentRepository.has(name):
            return None

        return fork_component\
            and ComponentRepository.fork(name)\
            or ComponentRepository.get(name)

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

    _logger = getLogger('%s.ResourceService' % (__name__), logging.ERROR)

    _patterns      = {}
    _pattern_order = []
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
        ResourceService._logger.error('add URL pattern "%s" for "%s"' % (pattern, base_path))
        ResourceService._patterns[pattern] = base_path
        ResourceService._pattern_order.append(pattern)

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
            self._logger.error('Retrieving from the wildcard pattern')

            resource = self._get_resource_on_non_precalculated_pattern(path)

        # Get the content type.
        self.set_header("Content-Type", resource.kind or 'text/plain')

        # Return HTTP 404 if the content is not found.
        if not resource.exists:
            self._logger.error('%s could not be found.' % resource.path)

            raise HTTPError, 404

        # Retrieve the plugins if registered.
        if not ResourceService._plugins and not ResourceService._plugins_registered:
            ResourceService._plugins = ComponentRepository.find_by_tag(
                ResourceService._plugins_tag_name
            )

        # Apply the plugin.
        for plugin in ResourceService._plugins:
            if plugin.expect(resource):
                resource = plugin.execute(resource)
            # End the iteraltion

        # Return the content.
        try:
            self.finish(resource.content)
        except Exception, e:
            print 'Failed on resource distribution.'
            print e, type(e)

    def _get_resource_entity(self, real_path):
        return ResourceEntity(real_path)

    def _get_resource_on_non_precalculated_pattern(self, path_to_resource):
        request_uri = self.request.uri

        for pattern in ResourceService._pattern_order:
            base_path = ResourceService._patterns[pattern]

            self._logger.debug('Comparing Pattern: %s' % pattern)

            matches = match(pattern, request_uri)

            if not matches:
                continue

            used_pattern = pattern
            real_path    = p.abspath(p.join(
                base_path,
                matches.groups()[0]
            ))

            self._logger.info('Real path: %s' % real_path)

            return self._get_resource_entity(real_path)

        raise HTTPError, 404