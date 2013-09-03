# -*- coding: utf-8 -*-

"""
:Author: Juti Noppornpitak

This package contains an abstract controller (based on
:class:`tornado.web.RequestHandler`) and built-in controllers.
"""

import logging

from base64 import b64decode
from os import path as p
from re import match, sub

from jinja2.exceptions import TemplateNotFound
from tornado.web import HTTPError, RequestHandler

from tori.centre             import services
from tori.common             import get_logger
from tori.data.base          import ResourceEntity, resolve_file_path
from tori.exception          import *
from tori.template.renderer  import DefaultRenderer
from tori.session.generator  import GuidGenerator
from tori.session.controller import Controller as SessionController

class Controller(RequestHandler):
    """
    The abstract controller for Tori framework which uses Jinja2 as a template
    engine instead of the default one that comes with Tornado.
    """

    _guid_generator  = GuidGenerator()
    _template_engine = None


    def __init__(self, *args, **kwargs):
        RequestHandler.__init__(self, *args, **kwargs)

        self._session = None

    @property
    def is_xhr(self):
        return 'X-Requested-With' in self.request.headers and self.request.headers['X-Requested-With'] == 'XMLHttpRequest'

    def component(self, name, fork_component=False):
        """
        Get the (re-usable) component from the initialized Imagination
        component locator service.

        :param `name`:           the name of the registered re-usable component.
        :param `fork_component`: the flag to fork the component
        :return:                 module, package registered or ``None``
        """

        if not services.has(name):
            return None

        return services.fork(name)\
            if   fork_component\
            else services.get(name)

    @property
    def session(self):
        """ Session Controller

        :rtype: tori.session.controller.Controller
        """
        if not self.component('session'):
            return None

        if self._session:
            return self._session

        cookie_key = 'ssid'

        ssid = self.get_secure_cookie(cookie_key)\
            if   self._can_use_secure_cookie()\
            else self.get_cookie(cookie_key)

        if not ssid:
            ssid = self._guid_generator.generate()

            if self._can_use_secure_cookie():
                self.set_secure_cookie(cookie_key, ssid)
            else:
                self.set_cookie(cookie_key, ssid)

        self._session = SessionController(self.component('session'), ssid)

        return self._session

    def _can_use_secure_cookie(self):
        """
        Check if the secure cookie is enabled.

        :rtype: boolean

        .. note::
            This only works with any classes based from :class:`tornado.webRequestHandler`
            and :class:`tornado.websocket.WebSocketHandler`.

        """
        return 'cookie_secret' in self.settings and self.settings['cookie_secret']

    def render_template(self, template_name, **contexts):
        """
        Render the template with the given contexts.

        See :meth:`tori.renderer.Renderer.render` for more information.
        """

        # If the rendering source isn't set, break the code.
        if not self._template_base_path:
            raise RenderingSourceMissingError('The source of template is not identified. This method is disabled.')

        # If the rendering engine is not specified, use the default one.
        if not self._template_engine:
            self._template_engine = DefaultRenderer

        contexts['app'] = {
            'request': self.request,
            'session': self.session.get
        }

        output = self.template_engine.render(template_name, **contexts)

        if not output:
            raise UnexpectedComputationError('Detected the rendering service malfunctioning.')

        return output

    def render(self, template_name, **contexts):
        """
        Render the template with the given contexts and push the output buffer.

        See :meth:`tori.renderer.Renderer.render` for more information.
        """
        self.write(self.render_template(template_name, **contexts))

    @property
    def template_engine(self):
        """ Template Engine

        :rtype: tori.template.renderer.Renderer
        """

        # If the rendering engine is not specified, use the default one.
        if not self._template_engine:
            self._template_engine = DefaultRenderer

        try:
            return self.component('renderer').use(self._template_base_path)
        except RendererNotFoundError:
            # When the renderer is not found. It is possible that the renderer is not yet
            # instantiated. This block of the code will do the lazy loading.
            renderer = self._template_engine(self._template_base_path)

            self.component('renderer').register(renderer)

            return renderer

class SimpleController(Controller):
    """ Simplified Request Controller """
    def rendering_prefix(self):
        return None

    def get(self, *args):
        path = args[0] if args else 'index'

        if '..' in path:
            raise HTTPError(403)

        if '/' == path[-1]:
            path = 'index'

        rendering_path = '{}.html'.format(path)

        if self.rendering_prefix():
            rendering_path = p.join(self.rendering_prefix(), rendering_path)

        try:
            rendered_data = self.render_template(rendering_path)
        except TemplateNotFound as e:
            raise HTTPError(404)

        if not rendered_data:
            raise HTTPError(404)

        self.write(rendered_data)

class RestController(Controller):
    """ Abstract REST-capable controller based on a single primary key. """
    def list(self):
        """ Retrieve the list of all entities. """
        self.set_status(405)

    def retrieve(self, id):
        """ Retrieve an entity with `id`. """
        self.set_status(405)

    def create(self):
        """ Create an entity. """
        self.set_status(405)

    def remove(self, id):
        """ Remove an entity with `id`. """
        self.set_status(405)

    def update(self, id):
        """ Update an entity with `id`. """
        self.set_status(405)

    def get(self, id=None):
        """ Handle GET requests. """
        if not id:
            self.list()
            return

        self.retrieve(id)

    def post(self, id=None):
        """ Handle POST requests. """
        if id:
            self.set_status(405)
            return

        self.create()

    def put(self, id=None):
        """ Handle PUT requests. """
        if not id:
            self.set_status(400)
            return

        self.update(id)

    def delete(self, id=None):
        """ Handle DELETE requests. """
        if not id:
            self.set_status(400)
            return

        self.remove(id)

class ErrorController(Controller):
    """Generates an error response with status_code for all requests."""
    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        raise HTTPError(self._status_code)

class ResourceService(Controller):
    """ Resource service is to serve a static resource via HTTP/S protocol. """

    _logger = get_logger('%s.ResourceService' % (__name__), logging.ERROR)

    _favicon_data = b64decode(''.join([
        'AAABAAEAEBAQAAAAAAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAA',
        'AAAAEAAAAAAAAAAAAAAA/4QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAARAAAAAAAAABEQAAAAAAAAEREA',
        'AAAAAAARERAAAAAAABEREQAAAAAAEREREAAAAAARERERAAAAABEREREQAAAAEREREREA',
        'AAARERERERAAABEREREREQAAEREREREREAARERERERERABEREREREREQERERERERERF/',
        '/wAAP/8AAB//AAAP/wAAB/8AAAP/AAAB/wAAAP8AAAB/AAAAPwAAAB8AAAAPAAAABwAA',
        'AAMAAAABAAAAAAAA'
    ]))

    _patterns      = {}
    _pattern_order = []
    _cache_objects = {}

    _plugins            = {}
    _plugins_tag_name   = 'resource-service-plugin'
    _plugins_registered = False

    @staticmethod
    def add_pattern(pattern, base_path, enable_cache=False):
        """
        Add the routing pattern for the resource path prefix.

        :param pattern: a routing pattern. It can be a Python-compatible regular expression.

        :param base_path: a path prefix of the resource corresponding to the routing pattern.

        :param enable_cache: a flag to indicate whether any loaded resources need to be cached on the first request.
        """
        ResourceService._logger.debug('add URL pattern "%s" for "%s"' % (pattern, base_path))
        ResourceService._patterns[pattern] = {
            'base_path': resolve_file_path(base_path),
            'cacheable': enable_cache
        }
        ResourceService._pattern_order.append(pattern)

    def get(self, path=None):
        """
        Get a particular resource.

        :param path: blocks of path used to composite an actual path.

        .. note::
            This method requires refactoring.
        """
        resource = self._retrieve_resource_entity()

        if isinstance(resource, str):
            self.set_header('Content-Type', 'image/vnd.microsoft.icon')
            return self.finish(resource)
        elif resource.exists and resource.cacheable:
            self._cache_objects[self.request.uri] = resource
        elif not resource.exists:
            # Return HTTP 404 if the content is not found.
            self._logger.error('%s could not be found.' % resource.path)

            raise HTTPError(404)

        # Get the content type.
        self.set_header("Content-Type", resource.kind or 'text/plain')

        # Retrieve the plugins if registered.
        if not ResourceService._plugins and not ResourceService._plugins_registered:
            ResourceService._plugins = services.find_by_tag(
                ResourceService._plugins_tag_name
            )

        # Apply the plugin.
        for plugin in ResourceService._plugins:
            if plugin.expect(resource):
                resource = plugin.execute(resource)
            # End the iteration

        # Return the content.
        try:
            self.finish(resource.content)
        except Exception as e:
            raise HTTPError(500)

    def _retrieve_resource_entity(self):
        request_uri = self.request.uri
        path        = sub('\?.*$', '', request_uri)

        if request_uri in self._cache_objects:
            return self._cache_objects[request_uri]

        # If the request URI is already pre-calculated or fixed, load the
        # entity from the corresponding path.
        elif request_uri in ResourceService._patterns:
            pattern = ResourceService._patterns[request_uri]

            return self._create_resource_entity(pattern['base_path'], pattern['cacheable'])

        # When the resource is not loaded, try to get from the wildcard pattern.
        self._logger.debug('Retrieving from the wildcard pattern.')

        return self._get_resource_on_non_precalculated_pattern(path)

    def _create_resource_entity(self, real_path, cachable):
        return ResourceEntity(real_path, cachable)

    def _get_resource_on_non_precalculated_pattern(self, request_uri):
        for pattern in ResourceService._pattern_order:
            pattern_info = ResourceService._patterns[pattern]

            base_path = pattern_info['base_path']
            cachable  = pattern_info['cacheable']

            self._logger.debug('Comparing Pattern: %s' % pattern)

            matches = match(pattern, request_uri)

            if not matches:
                continue

            real_path = p.abspath(p.join(
                base_path,
                matches.groups()[0]
            ))

            self._logger.info('Real path: %s' % real_path)

            return self._create_resource_entity(real_path, cachable)

        if self.request.uri == '/favicon.ico':
            return self._favicon_data

        raise HTTPError(404)