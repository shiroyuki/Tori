# -*- coding: utf-8 -*-

"""
:Author: Juti Noppornpitak

..note::
    The documentation of this module yet conforms with the standard documenting
    style used by the official Python documenters.
"""

# Standard libraries
import json
import os
import sys

# Third-party libraries
from imagination.entity  import Entity as ImaginationEntity, CallbackProxy
from imagination.helper  import retrieve_module_path
from imagination.loader  import Loader as ImaginationLoader
from imagination.locator import Locator as ImaginationLocator
from imagination.helper.assembler import Assembler   as ImaginationAssembler
from imagination.helper.data      import Transformer as ImaginationTransformer
from kotoba             import load_from_file
from tornado.autoreload import watch
from tornado.ioloop     import IOLoop
from tornado.web        import Application as TornadoNormalApplication
import tornado.web
from tornado.wsgi       import WSGIApplication as TornadoWSGIApplication
from wsgiref            import handlers

# Internal libraries
from tori            import centre
from tori.centre     import settings as AppSettings
from tori.centre     import services as AppServices
from tori.common     import get_logger
from tori.data.base  import resolve_file_path
from tori.exception  import *
from tori.navigation import *

class BaseApplication(object):
    """
    Interface to bootstrap a WSGI application with Tornado Web Server/Framework.
    This is the basic application class which practically does nothing. Please
    do not use this directly.

    :param `settings`: variable key-value parameters for extra settings to
    Tornado Web Server / Framework. Please read the web server documentation
    for more details.
    """

    _default_config_tree = {
        "session": {
            "class": "tori.session.repository.memory.Memory",
            "params": {}
        },
        "db": {
            "managers": {}
        }
    }

    def __init__(self, **settings):
        self._logger = get_logger('{}.{}'.format(__name__, self.__class__.__name__))

        self._hierarchy_level = len(self.__class__.__mro__) - 1

        self._ioloop = IOLoop.instance()

        settings.update(self._default_config_tree)

        # Setting for the application.
        self._settings          = settings
        self._settings['debug'] = False
        self._listening_addr    = '0.0.0.0'
        self._listening_port    = 8888

        if 'base_path' not in self._settings:
            # Get the reference to the calling function
            current_function    = sys._getframe(self._hierarchy_level)
            caller_function     = current_function.f_code
            reference_to_caller = caller_function.co_filename

            # Base path
            self._base_path = os.path.abspath(os.path.dirname(os.path.abspath(reference_to_caller)))
            self._base_path = 'static_path' in settings and settings['static_path'] or self._base_path

            self._settings['base_path'] = self._base_path

        self._base_path = self._settings['base_path']

        self._static_routing_setting = dict(path=self._base_path)
        self._routes = []

        # Enable the reverse reference
        disabled_core_reference = 'disabled_core_reference' in settings and settings['disabled_core_reference']

        if not disabled_core_reference and not centre.core:
            centre.core = self

    @property
    def base_path(self):
        return self._base_path

    def _update_routes(self, routes):
        """
        Update the routes.

        `routes` is the list of routes. See Tornado documentation on `tornado.web.Application` for more detail.
        """
        self._routes = routes

    def _activate(self):
        """
        Activate the backend application.
        """

        # Update the global settings.
        AppSettings.update(self._settings)

        # Instantiate the backend application.
        self._backend_app = TornadoNormalApplication(self._routes, **self._settings)

    def listen(self, port_number=None, bind_address=None):
        """
        Tell the app to listen on the given port number.

        `port_number` is an integer to indicate which port the application should be listen to.
        This setting is however only used in a standalone mode.
        """

        if port_number:
            self._listening_port = int(port_number)

        if bind_address:
            self._listening_addr = bind_address

        self._logger.debug('Listen at {} on port {}.'.format(self._listening_addr, self._listening_port))

        return self

    def add(self, callable_reference, timeout=500):
        self._ioloop.add_timeout(timeout, callable_reference)

    def start(self):
        """
        Start a server/service.
        """
        try:
            self._backend_app.listen(self._listening_port, self._listening_addr)

            self._logger.info("Start the application based at %s." % self._base_path)
            self._ioloop.start()
        except KeyboardInterrupt:
            self._logger.debug("Cleanly stopped.")

    def get_backbone(self):
        return self._backend_app

    def get_listening_port(self):
        return self._listening_port

class Application(BaseApplication):
    """
    Interface to bootstrap a WSGI application with Tornado Web Server.

    `settings` is a dictionary of extra settings to Tornado engine. For more
    information, please read Tornado documentation.
    """

    _registered_routing_types = ['controller', 'proxy', 'redirection', 'resource']
    _default_services         = [
        ('finder',      'tori.common.Finder',                     [], {}),
        ('renderer',    'tori.template.service.RenderingService', [], {}),
        ('session',     'tori.session.repository.memory.Memory',  [], {}),
        ('routing_map', 'tori.navigation.RoutingMap',             [], {}),
        ('db',          'passerine.db.manager.ManagerFactory',    [], {})
    ]

    _data_transformer         = ImaginationTransformer(ImaginationLocator())

    def __init__(self, configuration_location, **settings):
        BaseApplication.__init__(self, **settings)

        self._service_assembler = ImaginationAssembler(ImaginationTransformer(AppServices))
        self._config_main_path = os.path.join(self._base_path, configuration_location)
        self._config_base_path = os.path.dirname(self._config_main_path)

        self._config = load_from_file(self._config_main_path)

        # Initialize the routing map
        self._routing_map = RoutingMap()

        # Default properties
        self._scope = settings['scope'] if 'scope' in settings else None
        self._port  = 8000

        # Register the default services.
        self._register_default_services()

        # Add the main configuration to the watch list.
        watch(self._config_main_path)

        # Configure with the configuration files
        self._service_assembler.activate_passive_loading()

        for inclusion in self._config.children('include'):
            self._load_inclusion(inclusion)

        self._configure(self._config)

        self._prepare_db_connections()
        self._prepare_session_manager()

        self._service_assembler.deactivate_passive_loading()

        # Override the properties with the parameters.
        if 'port' in settings:
            self._port = settings['port']
            self._logger.info('Changed the listening port: %s' % self._port)

        # Update the routing map
        AppServices.get('routing_map').update(self._routing_map)

        # Normal procedure
        self._update_routes(self._routing_map.export())
        self.listen(self._port)
        self._activate()

    def _prepare_session_manager(self):
        config = self._settings['session']

        self._set_service_entity('session', config['class'], **config['params'])

    def _prepare_db_connections(self):
        db_config = self._settings['db']
        manager_config = db_config['managers']
        em_factory = AppServices.get('db')

        for alias in manager_config:
            url = manager_config[alias]['url']

            em_factory.set(alias, url)

            def callback(em_factory, db_alias):
                return em_factory.get(db_alias)

            callback_proxy = CallbackProxy(callback, em_factory, alias)

            AppServices.set('db.{}'.format(alias), callback_proxy)

    def _load_inclusion(self, inclusion):
        source_location = inclusion.attribute('src')

        if source_location[0] != '/':
            source_location = os.path.join(self._config_base_path, source_location)

        pre_config = load_from_file(source_location)

        self._configure(pre_config, source_location)

        watch(source_location)

        self._logger.info('Included the configuration from %s' % source_location)

    def _load_new_style_configuration(self, configuration):
        # Load the data directly from a JSON file.
        for inclusion in configuration.children('use'):
            source_location = inclusion.attribute('src')

            if source_location[0] != '/':
                source_location = os.path.join(self._config_base_path, source_location)

            with open(source_location) as f:
                decoded_config = json.load(f)

                self._override_sub_config_tree(self._settings, decoded_config)

                watch(source_location)

    def _override_sub_config_tree(self, original_subtree, modified_subtree):
        for key in modified_subtree:
            if key not in original_subtree:
                original_subtree[key] = modified_subtree[key]
                continue

            original_node_type = type(original_subtree[key])
            modified_node_type = type(modified_subtree[key])

            if original_node_type is dict:
                if modified_node_type != original_node_type:
                    raise ValueError('The overriding configuration tree does not align with the predefined one.')

                self._override_sub_config_tree(original_subtree[key], modified_subtree[key])

                continue

            original_subtree[key] = modified_subtree[key]

    def _configure(self, configuration, config_path=None):
        if len(configuration.children('server')) > 1:
            raise InvalidConfigurationError('Too many server configuration.')

        if len(configuration.children('routes')) > 1:
            raise InvalidConfigurationError('Too many routing configuration.')

        if len(configuration.children('settings')) > 1:
            raise InvalidConfigurationError('Too many setting groups (limited to 1).')

        self._load_new_style_configuration(configuration)

        # Then, load the legacy configuration. (Deprecated in 3.1)
        # Load the general settings
        for config in configuration.find('server config'):
            key  = config.attribute('key')
            kind = config.attribute('type')

            if not key:
                raise InvalidConfigurationError('Invalid server configuration key')

            self._settings[key] = self._data_transformer.cast(config, kind)

        # Set the cookie secret for secure cookies.
        client_secret = configuration.find('server secret')

        if client_secret:
            self._settings['cookie_secret'] = client_secret.data()

        # Set the port number.
        port = configuration.find('server port')

        if len(port) > 1:
            raise DuplicatedPortError()
        elif port:
            self._port = port.data()

        # Find the debugging flag
        if (configuration.find('server debug')):
            self._settings['debug'] = configuration.find('server debug').data().lower() == 'true'
            self._logger.info('Debug Mode: {}'.format('On' if self._settings['debug'] else 'Off'))

        for setting in configuration.children('settings').children('setting'):
            setting_name = setting.attr('name')

            if not setting_name:
                raise InvalidConfigurationError('A setting block does not specify the name. ({})'.format(config_path or 'primary configuration'))

            self._settings[setting_name] = setting.data()

        # Exclusive procedures
        self._register_imagination_services(configuration, config_path or self._config_base_path)
        self._map_routing_table(configuration)
        self._set_error_delegate(configuration)

    def _set_error_delegate(self, configuration):
        """ Set a new error delegate based on the given configuration file if specified. """
        delegate = configuration.find('server error').data()

        if delegate:
            self._logger.info('Custom Error Handler: %s' % delegate)
            tornado.web.ErrorHandler = ImaginationLoader(delegate).package

    def _register_default_services(self):
        for id, package_path, args, kwargs in self._default_services:
            try:
                self._set_service_entity(id, package_path, *args, **kwargs)
            except ImportError as exception:
                if id == "db":
                    self._logger.info('Ignored {} as package "passerine" is neither available or loadable (containing errors).'.format(package_path))

                    continue

                raise ImportError('Failed to register {} ({})'.format(id, package_path))

    def _register_imagination_services(self, configuration, base_path):
        """ Register services. """
        service_blocks = configuration.children('service')

        for service_block in service_blocks:
            service_config_path = service_block.data()

            # If the file path contains ':', treat the leading part for the full
            # module name and re-assembles the file path.

            config_file_path = resolve_file_path(service_config_path)

            if service_config_path[0] != '/':
                config_file_path = os.path.join(base_path, service_config_path)

            self._logger.info('Loading services from {}'.format(config_file_path))

            self._service_assembler.load(config_file_path)

    def _map_routing_table(self, configuration):
        """
        Update a routing table based on the configuration.
        """
        routing_sequences = configuration.children('routes')

        self._logger.debug('Registering the routes from the configuration...')

        if not routing_sequences:
            return

        # Register the routes to controllers.
        for routing_sequence in routing_sequences:
            new_routing_map = RoutingMap.make(routing_sequence, self._base_path)

            self._routing_map.update(new_routing_map)

        self._logger.debug('Registered the routes from the configuration.')

    def _make_service_entity(self, id, package_path, *args, **kwargs):
        """
        Make and return a service entity.

        *id* is the ID of a new service entity.

        *package_path* is the package path.

        *args* and *kwargs* are parameters used to instantiate the service.
        """
        loader = ImaginationLoader(package_path)
        entity = ImaginationEntity(id, loader, *args, **kwargs)

        return entity

    def _set_service_entity(self, id, package_path, *args, **kwargs):
        """
        Set the given service entity.

        *id* is the ID of a new service entity.

        *package_path* is the package path.

        *args* and *kwargs* are parameters used to instantiate the service.
        """
        AppServices.set(id, self._make_service_entity(id, package_path, *args, **kwargs))

    def get_route(self, routing_pattern):
        """ Get the route. """
        return self._routing_map.find_by_pattern(routing_pattern)

class WSGIApplication(Application):
    """
    Interface to bootstrap a WSGI application with Apache WSGI module.

    This class is simply a clone to :class:`Application` except that it is
    specially customized for deploying the application in the WSGI embedded mode.
    """

    def __init__(self, configuration_location, **settings):
        Application.__init__(self, configuration_location, **settings)

    def _activate(self):
        """
        Activate the backend application.
        """

        # Update the global settings.
        AppSettings.update(self._settings)

        # Instantiate the backend application.
        self._backend_app = TornadoWSGIApplication(self._routes, **self._settings)

    def start(self):
        """
        Start the process.

        .. warning:: This method is only necessary for a Google App Engine.
        """
        handlers.CGIHandler().run(self.get_backbone())
