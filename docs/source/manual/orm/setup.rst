Getting Started
***************

The chapter illustrates how to define entities and set up an entity manager.

Define an Entity
================

First, we define the entity (document) class.

.. code-block:: python

    from tori.db.entity import entity

    # Alternatively, @entity('name_of_collection') is to set the name of the collection.
    @entity
    class Character(object):
        def __init__(self, name):
            self.name = name

where an entity of class ``Character`` automatically has a readable and writable property ``id`` which can be set
only once.

.. warning:: It is not recommended to the ID manually. Leave setting the ID to the backend database.

Define the Entity Manager
=========================

Then, define the entity manager.

.. code-block:: python

    from pymongo import Connection
    from tori.db.manager import Manager

    connection = Connection()
    entity_manager = Manager('default')