Configuration
*************

:Author: Juti Noppornpitak

The configuration in Tori framework is written on XML. The only reason is because it is validable and flexible. It is largely
influenced by the extensive uses of JavaBeans in Spring Framework (Java) and the lazy loading in Doctrine (PHP).

Specification
=============

Here is the complete specification of the configuration file::

    permitive_boolean ::= 'true' | 'false'

    root_node ::= '<application>' include_node server_node routing_node service_node '</application>'

    # Include other configuration files
    include_node ::= '<include src="' include_file_path '"/>' include_node | ''
    # "include_file_path" is a string representing either an absolute path or a relative path to the current
    # working directory of the script.

    # Server-specific configuration
    server_node ::= '<server>' server_debug_node server_port_node server_error_node '</server>' | ''

    server_config_node ::= (
            server_debug_node
            | server_port_node
            | server_error_node
        )
        server_config_node

    # Debug switch (which can be overridden by the app constructor)
    server_debug_node ::= '<debug>' permitive_boolean '</debug>' | ''
    # Default to "true"

    # Server port number
    server_port_node ::= '<port>' server_port_number '</port>' | ''
    # E.g., 80, 443, 8000 (default) etc.

    # Custom error delegate/handler as a controller.
    server_error_node ::= '<error>' server_error_class '</error>' | ''
    # "server_error_class" is a string representing the full name of the error controller class, for instance,
    # com.shiroyuki.www.controller.ErrorController. If not specified, the default handler will be decided by
    # Tornado's code.

    # Routing configuration
    routing_node ::= '<routes>' routing_route_node '</routes>'

    routing_route_node ::= (
            routing_route_controller_node
            | routing_route_redirection_node
            | routing_route_resource_node
        )
        routing_route_node
        | ''

    tornado_route_pattern ::= 'pattern="' tornado_route_pattern_regexp '"'

    # "controller_class" is a string representing the full name of the controller class, for instance,
    # com.shiroyuki.www.controller.HomeController.

    # Controller
    routing_route_controller_node ::= '<controller class="' controller_class '" ' tornado_route_pattern '/>'

    # Redirection
    routing_route_redirection_node ::= '<redirection destination="' tornado_route_pattern '" ' tornado_route_pattern '/>'

    # Resource
    routing_route_resource_node ::= '<resource location="' file_path_pattern '" ' tornado_route_pattern ' cache="' permitive_boolean '"/>'

    # Service configuration
    service_node ::= '<service>' include_file_path '</service>' service_node | ''

.. note:: DTD will be provided as soon as someone is willing to help out on writing.

You can see the example from `the configuration <https://github.com/shiroyuki/Council/tree/master/council/config>`_ of
The Council Project on GitHub.

See More
========

.. toctree::
   :maxdepth: 1
   :glob:

   *
