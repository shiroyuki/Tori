Routing
*******

The routes (``<routes>``) is prioritized by the order in the routing list.

There are 4 types of routes are supported.

=========== =================================================================
Directive   Description
=========== =================================================================
controller  A routing directive for dynamic content handled by a controller.
resource    A routing directive for static content/resource.
redirection A routing directive for relaying requests with redirection.
proxy       A routing directive for proxying requests.
=========== =================================================================

In general, the attribute ``pattern`` of any routing directives is to indicate the routing pattern where the directive intercepts,
process and respond to any requests to the pattern. Each routing pattern is unique from each other.

Controller
==========

For a routing directive ``controller``, the attribute ``class`` is a class reference to a particular controller where the
controller must be on the system path (for Python).

.. code-block:: xml

    <controller class="app.note.controller.IndexController" pattern="/notes/(.*)"/>

Redirection
===========

For a routing directive ``redirection``, the attribute ``destination`` is a string indicating the destination of the redirection,
and the attribute ``permanent`` is a boolean indicating whether the redirection is permanent.

.. code-block:: xml

    <redirection destination="/notes/" pattern="/notes"/>

Resource
========

For a routing directive ``resource``, the attribute ``location`` is either:

* an absolute or relative path to static resource,
* a module name containing static resource.

the attribute ``cache`` is a boolean to indicate whether the resource should be cache.

.. code-block:: xml

    <resource location="resources/favicon.ico" pattern="/favicon.ico" cache="true"/>

.. warning::
    The directive ``proxy`` is not supported at this moment.

