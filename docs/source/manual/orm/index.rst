Object-relational Mapping (ORM)
*******************************

Tori Framework introduces the object-relational mapping module for MongoDB 2.0 or newer.

.. versionadded: 2.1
.. versionchanged: 2.1

.. toctree::
    :maxdepth: 3
    :glob:

    introduction
    setup
    basic-usage
    working-with-association
    handling-transactions
    *

Testing Environments
====================

The ORM is tested with the following configurations.

================= ===========================
MongoDB Version   Operating System / Platform
================= ===========================
2.2+              Mac OS X 10.8 Server
2.2+              GNU/Linux Debian*
2.2+              Fedora Core*
anything versions Travis CI
================= ===========================

.. note::

    Only test on the latest stable version of OSs running on the latest
    version of VirtualBox 4.2 on Mac OS X.

See also
========

* :doc:`/api/db/index`