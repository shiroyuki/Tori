Object-relational Mapping (ORM)
*******************************

Tori Framework introduces the object-relational mapping module for MongoDB which you may find the code in :mod:`tori.db`.

.. warning::

    Even though this feature is experimental, it is tested, stable and usable to use with some restrictions:

    * It currently does not works with association.
    * Filtering only restricted to exact matching.

Let's see from the example.

Setup
=====

First, we define the document class.

.. code-block:: python

    from tori.db.document import document

    @document
    class Character(object):
        def __init__(self, name, _id=None):
            self._id  = _id
            self.name = name

Then, define the database.

.. code-block:: python

    from tori.db.database import Database

    db = Database('final_fantasy_tactics')

Then, define the target collection.

.. code-block:: python

    from tori.db.collection import Collection

    character_collection = Collection(db, Character, 'character')

Create a Document
=================

Now, let's create two characters (documents), "Ramza" and "Alma", in the collection.

.. code-block:: python

    ramza = Character('Ramza', 1)
    alma  = Character('Alma', 2)

    character_collection.post(ramza)
    character_collection.post(alma)

List, Query/filter Documents
============================

To list all characters (documents),

.. code-block:: python

    characters = character_collection.filter()

    for character in characters:
        print('{}: {}'.format(character.id, character.name))

Then, you should see::

    1: Ramza
    2: Alma

Now, to find "Ramza",

.. code-block:: python

    ramza = character_collection.filter(name='Ramza')

    for character in characters:
        print('{}: {}'.format(character.id, character.name))

Then, you should see::

    1: Ramza

Get a Document
==============

Now, to get by ID or MongoDB's ``ObjectId``,

.. code-block:: python

    alma = character_collection.get(2)

Update Documents
================

Let's say you want to rename "Alma" to "Luso".

.. code-block:: python

    character = character_collection.filter(name='Alma')

    character.name = 'Luso'

    character_collection.put(character)

Delete Documents
================

To delete a character (document) by ID,

.. code-block:: python

    character_collection.delete(2)

.. note:: in the future, it should work with objects.

See also
========

* :doc:`../api/db/index`