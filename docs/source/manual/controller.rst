Controller
**********

Tori's framework ships with a based controller, extending from ``tornado.web.RequestHandler``. So, the usage is
pretty much the same as you can find in Tornado's documentation.

Suppose we have the following file structure.::

    web/
        __init__.py
        controller.py
        views/
            index.html
            error.html

Create a Controller
===================

Let's start with create a controller in **web/controller.py**

.. code-block:: python

    # Module: web.controller (web/controller)
    from tori.controller import Controller

    class HomeController(Controller):
        def get(self, name):
            self.write('Hello, {}.'.format(name))

However, as mentioned earlier, the rendering engine is replaced with Jinja2. By default, the methods ``render``
and ``render_template`` of :doc:`controller` are not ready to use.

Enable the Template Engine
==========================

Template Engine in Tori Framework is **totally optional** but enabling is not a big problem.

Before getting started, the integration between the rendering part and the controller part is based on the concept
of flexibility where each controller can use any template engine or any source. For instance, two controllers may
use two different engines or sources.

First, the decorator ``tori.decorator.controller.renderer`` (or ``@renderer`` for short) must be imported.

.. code-block:: python

    from tori.decorator.controller import renderer

where the only parameter of ``@renderer`` is either the name of the package (``web.views``) or the file path
(**web/views**). In this example, we use the package.

.. note::

    The file path can be either relative with regard of the current working directory or absolute. However,
    using the package option is recommended.

Suppose the content of **web/views/index.html** is

.. code-block:: django

    Hello, {{ name }}

Then, we replace ``self.write(...)`` with

.. code-block:: python

    self.render('index.html', name=name)

There is only one default and reserved variable ``app`` with two attributes:

- ``app.request``: an instance of controller's request ``tornado.httpserver.HTTPRequest``
- ``app.session``: a reference to controller's session getter :class:`tori.session.controller.Controller`

Using Session
=============

Where Tornado framework provide nothing regarding to session management, Tori integrates the cookie-based session
controller.

.. note::

    The session controller works with both secure and non-secure cookies. The secure cookies are highly recommended.

The session controller for the session data for a particular session ID is accessible via the read-only property
``session`` of the controller. For example, to get a session key "userId", you can do by

.. code-block:: python

    self.session.get('userId')

from any method of the controller. Please read more from :class:`tori.session.controller.Controller`.

REST Controller
===============

Tori provides the base controller :class:`tori.controller.RestController` for CRUD operations. It is however designed
strictly for querying, creating, retrieving, updating and deleting data.

To use it, the route pattern must accept only one parameter where it is optional. For example, the route can be

.. code-block:: xml

    <controller class="web.controller.BlogEntryRestController" pattern="/blog/rest/entry/(.*)"/>

where ``web.controller.BlogEntryRestController`` is

.. code-block:: python

    class BlogEntryRestController(RestController):
        def list(self):
            # GET /blog/rest/entry/
            # query the list of entries

        def create(self):
            # POST /blog/rest/entry/
            # create a new entry

        def retrieve(self, id):
            # GET /blog/rest/entry/ID
            # retrieve the entry by ID

        def update(self, id):
            # PUT /blog/rest/entry/ID
            # update the entry by ID

        def remove(self, id)
            # DELETE /blog/rest/entry/ID
            # delete the entry by ID

.. note::

    The ``remove`` method is actual the replacement of the ``delete`` method but to minimize the need of users to call
    the parent/ancestors version of the overridden method, the ``delete`` method is tended to be left untouched where
    the deleting implementation should be placed in the ``remove`` method.

Customize Error Page
====================

To specify a custome error page to a particular controller, the decorator :method:`tori.decorator.controller.custom_error`
is necessary. For example,

.. code-block:: python

    @custom_error('error.html')
    @renderer('web.views')
    class HomeController(Controller):
        pass

The error template ``web/views/error.html`` will receive three variables: ``message``, ``code`` (HTTP Response Code) and
``debug_info`` (the text version of stack trace).

References
==========

For more information, please read

* :doc:`template` (Manual)
* :doc:`../api/controller`
* :doc:`../api/decorator.controller`
* :doc:`../api/renderer` (API)
* :doc:`../api/session`