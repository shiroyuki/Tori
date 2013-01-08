.. Tori documentation master file, created by
   sphinx-quickstart on Fri Feb 17 21:37:41 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tori Framework
==============

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>

Tori is a micro framework based on Facebook's Tornado framework 2.x and supports both Python 2.6+, including
Python 3.3+.

As you may know that there already exists number of web framework, Tori is made for the different purposes.

1. It is to simplify the setup process.
2. Everything in Tori, beside what Tornado provides, is designed for applications developed on the concepts of
   aspect-oriented programming (AOP) and dependency injections (DI) which heavily relies on `Imagination Framework <https://github.com/shiroyuki/Imagination>`_.
3. Free to design the structure of the application in the way everyone wants.
4. Many built-in components are designed for re-usability with or without Tornado and Imagination Framework.

Even though Tori is based on Tornado, there are a few elements that differ from the Tornado.

1. The setup script is different as Tori acts as a wrapper for Tornado's Application.
2. Tori uses `Jinja2 <http://jinja.pocoo.org/>`_ as template engine.
3. Tori's controller extends Tornado's ``RequestHandler`` with the integration with Tori's session controller.

.. toctree::
   :maxdepth: 1
   :glob:

   */index

Indices and Modules
===================

* :ref:`genindex`
* :ref:`modindex`

.. * :ref:`search`
