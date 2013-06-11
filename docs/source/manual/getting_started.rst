Getting Started
***************

Installation
============

There are options for the installation:

* Use PyPI to install by running ``sudo pip install tori``,
* Download or clone the source code and run ``make install`` or ``python setup.py install``.

.. tip::

    The second option is preserved for development or installing the pre-release
    package from the source code.

Hello, world... again?
======================

In our imagination, we want to write a dead simple app to just say "Hello" to someone.

Suppose we have **Tori** on the system path and the following project structure::

    project/
        app/
            __init__.py
            error.py
            views/
                (empty)
        resources/
            readme.txt
            city.jpg

First, we write a controller ``project/app/controller.py`` with::

    from tori.controller           import Controller
    from tori.decorator.controller import renderer

    @renderer('app.views')
    class MainController(Controller):
        def get(self, name):
            self.render('index.html', name=name)

``@renderer('app.views')`` is to indicate that the template is in ``app.views``
and ``self.render`` is to render a template at ``index.html`` in ``app.views``
with a context variable ``name`` from a query string.

.. note:: Read more on :doc:`controller`.

Next, we write a Jinja2 template ``project/app/views/index.html`` with:

.. code-block:: django

    <!doctype html>
    <html>
    <head>
        <title>Example</title>
    </head>
    <body>
        Hello, {{ name }}
    </body>
    </html>

.. note:: Read more on :doc:`template`.

Then, we need to write a configuration file. For this example, we will save to
at ``project/server.xml`` containing:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <application>
        <server>
            <port>8000</port>
        </server>
        <routes>
            <controller
                class="demo.app.controller.main.MainController"
                pattern="/{name}"
                regexp="false"
            />
            <resource
                location="resources"
                pattern="/resources/**"
                cache="true"
                regexp="false"
            />
            <redirection
                destination="http://shiroyuki.com"
                pattern="/about-shiroyuki"
            />
        </routes>
        <services/>
    </application>

.. tip::

    This example uses the simple routing pattern introduced in Tori 2.1. See
    :doc:`configuration/routing` for more detail.

.. note::

    See :doc:`configuration/index` for more information on the configuration.

Then, we write a bootstrap file at ``project/server.py`` containing::

    from tori.application import Application

    application = Application('server.xml')
    application.start()

Now, to run the server, you can simply just execute::

    python server.py

You should see it running.
