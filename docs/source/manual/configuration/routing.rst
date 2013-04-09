Routing
*******

Routing Order and Priority
==========================

The routes (``<routes>``) is prioritized by the order in the routing list.

Types of Directives
===================

There are *3 types* of routes being supported.

=========== =================================================================
Directive   Description
=========== =================================================================
controller  A routing directive for dynamic content handled by a controller.
resource    A routing directive for static content/resource.
redirection A routing directive for relaying requests with redirection.
=========== =================================================================

Common Attributes
=================

========= ==================================================================== =================================================
Attribute Description                                                          Expected Values
========= ==================================================================== =================================================
pattern   the routing pattern                                                  *regular expression* or *simple pattern* (string)
regexp    the flag to indicate whether the given routing pattern is simplified ``true`` or ``false`` (boolean)
========= ==================================================================== =================================================

Regular-expression Routing Pattern
----------------------------------

In general, the attribute ``pattern`` of any routing directives is to indicate the routing
pattern where the directive intercepts, process and respond to any requests to the pattern.
Each routing pattern is unique from each other.

Simple Routing Pattern
----------------------

.. versionadded:: 2.1

By default, similar to Tornado, Tori Framework uses the normal regular expression for routing.
However, this could introduce an error-prone routing table for anyone that does not know the
regular expression. Here is the syntax where the routing resolver considers in the following
presented order.

===================== ============================
Simple Pattern Syntax Equvalent Regular Expression
===================== ============================
``**``                ``(.+)``
``*``                 ``([^/]+)``
``{name}``            ``(?P<name>.+)``
===================== ============================

Here are the simple versions of routing patterns.

========================== ================================ ============================
Simple Pattern             Equivalent Regular Expression    Expected Parameter List/Map
========================== ================================ ============================
``/abc/def/ghi/**``        ``/abc/def/ghi/(.+)``            index ``0`` or the first key
``/abc/def/ghi/*/jkl``     ``/abc/def/ghi/([^/]+)/jkl``     index ``0`` or the first key
``/abc/def/ghi/{key}/jkl`` ``/abc/def/ghi/(?P<key>.+)/jkl`` key ``key``
========================== ================================ ============================

To enable the simple routing pattern, the ``regexp`` attribute must be ``false`` (not default).

Default Routes for FAVICON
--------------------------

.. versionadded:: 2.1

In addition to the simple routing, the default route for ``/favicon.ico`` is available if not assigned.

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
