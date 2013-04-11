Basic Usage
***********

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

You can update this by

.. code-block:: python

    collection.put(character)

Delete entities
===============

.. code-block:: python

    collection.delete(alma)
