Getting Started
===============

:Author: Juti Noppornpitak

In our imagination, we want to write a dead simple app to just say "Hello" to someone.

Suppose we have **Tori** on the system path and the following project structure::

    project/
        app/
            __init__.py
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

``@renderer('app.views')`` is to indicate that the template is in ``app.views`` and ``self.render`` is to render a template at
``index.html`` in ``app.views`` with a context variable ``name`` from a query string.

.. note::
    Unlike other WSGI-compatible frameworks, as Tori is based on Tornado which writes the output to the buffer. So, we return nothing
    for ``MainController.get(...)``, ``MainController.post(...)``, ``MainController.put(...)`` and ``MainController.delete(...)``.

Next, we write a Jinja2 template ``project/app/views/index.html`` with:

.. code-block:: django

    <!doctype html>
    <html>
    <head>Example</head>
    <body>Hello, {{ name }}</body>
    </html>

Then, we need to write a configuration file. For this example, we will save to at ``project/server.xml`` containing:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <application>
        <server>
            <port>8000</port>
        </server>
        <routes>
            <controller class="demo.app.controller.main.MainController" pattern="/([^/]+)"/>
            <resource location="resources" pattern="/resources(/.*)" cache="true"/>
            <redirection destination="http://shiroyuki.com" pattern="/about-shiroyuki"/>
        </routes>
        <services/>
    </application>

See :doc:`configuration/index` for more information on the configuration.

Then, we write a bootstrap file at ``project/server.py`` containing::

    from tori.application import DIApplication

    application = DIApplication('server.xml')
    application.start()

Now, to run the server, you can simply just execute::

    python server.py

You should see it running.
