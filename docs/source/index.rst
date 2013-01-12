.. Tori documentation master file, created by
   sphinx-quickstart on Fri Feb 17 21:37:41 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tori Framework
==============

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>

Tori is a micro framework based on Facebook's Tornado framework 2.x and supports both Python 2.6+, including Python 3.3+.

Differences in Idea
-------------------

As you may know that there already exists number of web framework, Tori is made for the different purposes.

1. It is to simplify the setup process.
2. Everything in Tori, beside what Tornado provides, is designed for applications developed on the concepts of
   aspect-oriented programming (AOP) and dependency injections (DI) which heavily relies on `Imagination Framework
   <https://github.com/shiroyuki/Imagination>`_.
3. Free to design the structure of the application in the way everyone wants.
4. Many built-in components are designed for re-usability with or without Tornado and Imagination Framework.

Differences in Code
-------------------

Even though Tori is based on Tornado, there are a few elements that differ from the Tornado.

1. The setup script is different as Tori acts as a wrapper for Tornado's Application.
2. Tori Framework uses `Jinja2 <http://jinja.pocoo.org/>`_ as the default template engine.
3. Tori Framework's controller extends Tornado's ``RequestHandler`` with the integration with Tori's session controller.
4. Tori Framework can define more than one route to static resource.

Prerequisites
-------------

======================= ==============================
Module                  Required Third-party Modules
======================= ==============================
:mod:`tori.application` tornado 2.4+
:mod:`tori.controller`  tornado 2.4+
:mod:`tori.socket`      tornado 2.4+
:mod:`tori.db`          pymongo 2.3+ / sqlalchemy 0.7+
:mod:`tori.session`     redis 2.7+
:mod:`tori.template`    jinja2 2.6+
======================= ==============================

.. note:: It is not required to have all of them. You can install only what you need.

Installation
------------

Here is how you can install it.

Python 3.3 or Higher
********************

For **Python 3.3+**, as the setup configuration is not ready, you can simply download the source code and dump into your
Python path (e.g., ``PYTHONPATH`` on Linux, OS X and UNIX).

Python 2.7
**********

For **Python 2.7**, you can install via **PIP** command or **easy_install** command or you can download the source code
and run ``python setup.py install``. Just make sure you get the right version.

.. note::

    There is no plan on supporting the legacy releases of Python as the project moves forward to Python 3. Python 2.7 is
    the only series supported by the project.

Table of Content
----------------

.. toctree::
   :maxdepth: 1
   :glob:

   manual/index
   api/index

Indices and Modules
-------------------

* :ref:`genindex`
* :ref:`modindex`

.. * :ref:`search`
