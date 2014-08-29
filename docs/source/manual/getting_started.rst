Getting Started
***************

Installation
============

Just run ``sudo pip install tori``

Hello, world... again?
======================

After the installation, you can begin creating a app with the supplied ``nest``
command. In this example, we create an app called "konota web".

.. code-block:: bash

    nest tori.app.create -p 5000 konataweb

What just happened?

- The command generate a basic based on an app skeleton **at the working directory**.
- The option ``-p`` sets the default port to 5000.

At your current directory, you should see::

    (app root path)
        config/             <- config folder
            dev.xml         <- app config (routing)
            service.xml     <- config for service containers
            settings.json   <- app settings
        konataweb/          <- app module
            controller.py   <- dummy controller
        Makefile
        server.py           <- Bootstrap file
        static/             <- Just like Flask
            js/    (empty)
            image/ (empty)
            css/   (empty)
            scss/  (empty)
        templates           <- Just like Flask
            home.html       <- dummy template

If you take a look at :file:`konataweb/controller.py`, you will see::

    from tori.controller import Controller

    class Home(Controller):
        def get(self):
            self.render('home.html', name = 'konataweb')

where the base path of the template folder is at :file:`templates`.

.. note::

    The template engine is `Jinja2 <http://jinja.pocoo.org>`_.

.. note::

    You can re-define the base path of your template either by module (e.g.,
    `konataweb.templates` or :file:`/opt/templates`). For example, if you happened
    to have a template in :file:`konataweb/templates`, you can re-define by:

    1. import a decorator.

    .. code-block:: python

        from tori.decorator.controller import renderer

    2. decorate the controller to re-define the base path.

    .. code-block:: python

        @renderer('konataweb.templates')
        class Home(Controller):
            ...

Run ``make service`` to start the web service (not in the background). You should
now be able to access to http://localhost:5000.

What is a service container?
============================

In Tori Framework, you may define global variables for reusability. This part of
the framework is relied on `Project Imagination <https://github.com/shiroyuki/Imagination>`_
(see more information from the `documentation <http://imagination.readthedocs.org/en/latest/getting_started.html>`_).

For example, if we want to create a container (or known as **entity** in Project
Imagination) to do some calculation, first create :file:`konataweb.calculator.py`.

.. code-block:: python

    class EasyCalculator(object):
        def sum(self, *items):
            summation = 0

            for item in items:
                summation = item

            return item

Then, in :file:`config/service.xml`, just define an **entity** tag for a container
under ``<imagination>``.

.. code-block:: xml

    <entity id="easycalc" class="konataweb.calculator.EasyCalculator"/>
    <!-- You may define more than one container of the same class -->
    <entity id="different_easycalc" class="konataweb.calculator.EasyCalculator"/>

**To use the container in the controller or websocket handler**, you can simply
retrieve the global instance of the container **easycalc** by calling `self.component`.

.. code-block:: python

    # In konataweb/controller.py
    import re
    class CalculatorAPI(Controller):
        def get(self, operation):
            raw_nums = self.get_argument('num_sequence', '') # tornado.web.RequestHandler's original
            numbers  = [int(str_num) for str_num in re.split(',', raw_nums)]

            if operation != 'sum':
                return self.set_status(405) # tornado.web.RequestHandler's original

            sum = self.component('easycalc').sum(*numbers) # tori.controller.Controller's extra

            self.finish(sum)

Just now, we happen to have a new controller. We need to make it accessible.

Add a route
===========

To add a new route, just add a ``<controller>`` tag under ``<routes>``.

.. code-block:: xml

    <controller id="api.calculator" class="konataweb.controller.CalculatorAPI" pattern="/api/{operation}"/>

You should see the following result after you send a GET request to http://localhost:5000/api/sum?num_sequence=1,3,5,7::

    16

Application Settings (NEW since 3.0)
====================================

Instead of overriding the service container **session**, you achieve the same
thing by defining the section **session**. For example, we change to use the
file-based session.

.. code-block:: javascript

    {
        "session": {
            "class": "tori.session.repository.file.FileSessionRepository",
            "params": {
                "location": "session.json"
            }
        },
        ...
    }

Router in the template (NEW since 3.0)
======================================

In Tori 3, you can refer to any routes by ID. For instance, we add a link to the
calculator API.

.. code-block:: django

    <a href="{{ app.path('api.calculator', operation = 'sum') }}?num_sequence=1,3,5,7">Test link</a>

Read more
=========

- :doc:`controller`
- :doc:`orm/index`
- :doc:`configuration/routing`
- :doc:`configuration/index`
