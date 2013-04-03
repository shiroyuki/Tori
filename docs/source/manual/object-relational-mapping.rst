Object-relational Mapping (ORM)
*******************************

Tori Framework introduces the object-relational mapping module for MongoDB 2.0 or newer.

.. versionadded: 2.1

Architecture
============

There are a few points to highlight.

* The ORM uses the unit-of-work pattern.
* Although MongoDB does not has transaction support like MySQL, the ORM uses sessions to manage the object graph
  within the same memory space.

Setup
=====

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

Then, define the entity manager.

.. code-block:: python

    from pymongo import Connection
    from tori.db.manager import Manager

    connection = Connection()
    entity_manager = Manager('default')

Create a new entity
===================

Suppose two characters: "Ramza", and "Alma", are to created. The ORM provides two ways to create a new entity.

Using the constructor directly
------------------------------

.. code-block:: python

    ramza = Character('Ramza')
    alma  = Character('Alma')

    character_collection.post(ramza)
    character_collection.post(alma)

Using the "new" method
----------------------

.. code-block:: python

    session = entity_manager.open_session(supervised=False)
    collection = session.collection(Character)

    ramza = collection.new(name = 'Ramza')
    alma = collection.new(name = 'Alma')

    collection.post(ramza)
    collection.post(alma)

.. note:: for the following example, assume that ``ramza.id`` is ``1`` and ``alma.id`` is ``2``.

List, query or filter entities
==============================

To list all characters (documents),

.. code-block:: python

    characters = collection.filter()

    for character in characters:
        print('{}: {}'.format(character.id, character.name))

Then, you should see::

    1: Ramza
    2: Alma

Now, to find "Ramza",

.. code-block:: python

    characters = collection.filter({'name': 'Ramza'})

    for character in characters:
        print('{}: {}'.format(character.id, character.name))

Then, you should only see::

    1: Ramza

.. note::

    The criteria (e.g., in this case ``{'name': 'Ramza'}``) is the same one used by
    :class:`pymongo.collection.Collection`.

Retrieve an entity by ID
========================

Now, to retrieve an entity by ID,

.. code-block:: python

    alma = collection.get(2)

.. note::

    There is no auto-conversion from any given ID to :class:`bson.ObjectId` as the ID can be anything. If the ID of
    the target entity is of type :class:`bson.ObjectId`, e.g., ``"2"`` is a string representation of the
    ``ObjectId``, the code has to be ``alma = collection.get(bson.ObjectId('2'))``. (Assume that instantiating is okay.)

Update entities
===============

Let's say you want to rename "Alma" to "Luso".

.. code-block:: python

    alma = collection.get(2)

    alma.name = 'Luso'

    collection.put(character)

Delete entities
===============

.. code-block:: python

    collection.delete(alma)
    # or session.delete(alma)

Handling transaction
====================

Suppose one character named "Shun" must be created, and the user with ID 1 must be renamed back to "Umi". Here is an
example on how the transaction works.

.. code-block:: python

    # Let's use the same entity manager.
    session = entity_manager.open_session(supervised=False)
    collection = session.collection(Character)

    shun = collection.new(name='Shun')

    umi = collection.get(1)
    umi.name = 'Umi'

    collection.persist(shun)
    collection.persist(umi)
    # Alternatively, session.persist(...) works the same as collection's.

    collection.commit()
    # or session.flush()

.. note:: Both ``collection.commit`` and ``session.flush`` commit changes of the whole object graph.

(TODO: Write about associations)

See also
========

* :doc:`../api/db/index`