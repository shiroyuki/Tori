Introduction
************

Tori is a micro web framework, based on the latest release of Facebook's
Tornado Framework, and a collection of libraries, e.g. ORM for MongoDB. It
supports both Python 2.6, 2.7, and 3.3+.

Before using
------------

Please note that this framework/library is released under MIT license copyrighted
by Juti Noppornpitak. The distributed version of this license is available at
https://github.com/shiroyuki/Tori/blob/master/readme.md.

Differences in Idea
-------------------

As there already exists many web framework for Python, Tori Framework is made
for specific purposes.

1. It is to simplify the setup process and customizable.
2. Everything in Tori, beside what Tornado provides, is designed with the concepts
   of aspect-oriented programming (AOP) and dependency injections (DI) which
   heavily relies on `Imagination Framework <https://github.com/shiroyuki/Imagination>`_.
3. There is no guideline on how developers want to use the code.
4. Many libraries/components are designed for re-usability with or without the
   web framework part or Imagination Framework (AOP part).

Differences in Code
-------------------

Even though Tori is based on Tornado, there are a few elements that differ from
the Tornado.

1. The setup script is different as the setup process of Tori Framework is designed
   to be a wrapper for Tornado's Application.
2. Tori Framework overrides the default template engine with `Jinja2 <http://jinja.pocoo.org/>`_.
3. Tori Framework's controller extends Tornado's ``RequestHandler`` with the
   integration with Tori's session controller and the template engine.
4. Tori Framework can handle more than one route to static resource.
5. Provide a simple way to define routes. (added in 2.1)

Prerequisites
-------------

======================= ==============================
Module                  Required Third-party Modules
======================= ==============================
:mod:`tori.application` tornado 2.4+/3+
:mod:`tori.controller`  tornado 2.4+/3+
:mod:`tori.socket`      tornado 2.4+/3+
:mod:`tori.db`          pymongo 2.3+ / sqlalchemy 0.7+
:mod:`tori.session`     redis 2.7+
:mod:`tori.template`    jinja2 2.6+
======================= ==============================

.. note::

    It is not required to have all of them. You can keep only what you need.

Installation
------------

You can install via **PIP** command or **easy_install** command or you can
download the source code and run ``python setup.py install`` or ``make install``.

.. warning::

    There is no plan on supporting the legacy releases of Python as the project
    moves forward to **Python 3.3 or higher**. **Python 2.7** is the last series
    of Python 2 being supported by the project. **Python 2.6** seems to be working
    but ßthe framework is not tested.