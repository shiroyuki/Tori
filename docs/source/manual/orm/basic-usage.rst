Basic Usage
###########

Suppose we have::

    session   = entity_manager.open_session()
    char_repo = session.repository(Character)

Create a new entity
===================

Suppose two characters: "Ramza", and "Alma", are to created.

.. code-block:: python

    ramza = Character('Ramza')
    alma  = Character('Alma')

    character_repo.post(ramza)
    character_repo.post(alma)

.. note:: for the following example, assume that ``ramza.id`` is ``1`` and ``alma.id`` is ``2``.

List, query or filter entities
==============================

To list all characters (documents),

.. code-block:: python

    query      = char_repo.new_criteria('c')
    characters = char_repo.find(query)

    for character in characters:
        print('{}: {}'.format(character.id, character.name))

Then, you should see::

    1: Ramza
    2: Alma

Now, to find "Ramza",

.. code-block:: python

    query = char_repo.new_criteria('c')
    query.expect('c.name = :name')
    query.define('name', 'Ramza')

    characters = char_repo.find(query)

    for character in characters:
        print('{}: {}'.format(character.id, character.name))

Then, you should only see::

    1: Ramza

.. note::

    The queries use a simple query language. (If you see this message and see
    no explaination on the query language, please contact @shiroyuki on Twitter.)

Retrieve an entity by ID
========================

Now, to retrieve an entity by ID,

.. code-block:: python

    alma = char_repo.get(2)

.. note::

    There is no auto-conversion from any given ID to :class:`bson.ObjectId` as
    the ID can be anything. If the ID of the target entity is of type
    :class:`bson.ObjectId`, e.g., ``"2"`` is a string representation of the
    ``ObjectId``, the code has to be ``alma = collection.get(bson.ObjectId('2'))``.
    (Assume that instantiating is okay.)

Update entities
===============

Let's say you want to rename "Alma" to "Luso".

.. code-block:: python

    alma = collection.get(2)

    alma.name = 'Luso'

You can update this by

.. code-block:: python

    char_repo.put(character)

Delete entities
===============

.. code-block:: python

    char_repo.delete(alma)
