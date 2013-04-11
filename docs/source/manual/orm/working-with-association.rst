Working with Associations
*************************

This chapter introduces association mappings which directly use object IDs to
refer to the corresponding objects.

Tori only uses **decorators** (or annotations in some other languages) to define
the association mapping.

Instead of working with the object IDs directly, you will always work with
references to objects:

* A reference to a single object is represented by object IDs.
* A collection of objects is represented by many object IDs pointing to the
  object holding the collection

There are two sections in this chapter:

* types of associations
* options for associations

Types of Associations
=====================

In general, the decorator :meth:`tori.db.mapper.link` is used to define the
association a property of the decorated class to the another class.

For the sake of the simplicity of this chapter, all examples are assumed to
be in the module ``sampleapp.model``, and all begin with::

    from tori.db.entity import entity
    from tori.db.mapper import link, AssociationType as t

One-to-one
----------

Suppose there are two entities: A and B, **one-to-one associations** imply the
relationship between two entities as described in the following UML::

     A (1) ----- (1) B

Unidirectional
~~~~~~~~~~~~~~

Suppose we have two classes: ``Owner`` and ``Restaurant``, where ``Restaurant``
has the one-to-one unidirectional relationship with ``Owner``. 

.. code-block:: python

    @entity
    class Owner(object):
        def __init__(self, name):
            self.name  = name

    @link(
        target      = Owner, # or target = 'sampleapp.model.Owner'
        mapped_by   = 'owner',
        association = t.ONE_TO_ONE
    )
    @entity
    class Restaurant(object):
        def __init__(self, name, owner):
            self.name  = name
            self.owner = owner

where the structure of the stored document will be:

.. code-block:: javascript

    // note: object IDs are fake for demo.

    // collection: owner
    {'_id': 'owner-20130411129', 'name': 'siamese'}

    // collection: restaurant
    {'_id': ObjectId('1'), 'name': 'green curry', 'owner': 'owner-20130411129'}

Bidirectional
~~~~~~~~~~~~~

Suppose we have two classes: ``Owner`` and ``Restaurant``, where ``Restaurant``
has the one-to-one bidirectional relationship with ``Owner``.

.. code-block:: python

    @link(
        target      = 'sampleapp.model.Restaurant'
        mapped_by   = 'restaurant',
        association = t.ONE_TO_ONE,
        inverted_by = 'owner'
    )
    @entity
    class Owner(object):
        def __init__(self, name, restaurant):
            self.name       = name
            self.restaurant = restaurant

    @link(
        target      = Owner,
        mapped_by   = 'owner',
        association = t.ONE_TO_ONE
    )
    @entity
    class Restaurant(object):
        def __init__(self, name, owner):
            self.name  = name
            self.owner = owner

where the structure of the stored document will be:

.. code-block:: javascript

    // note: object IDs are fake for demo.

    // collection: owner
    {'_id': 'owner-20130411129', 'name': 'siamese'}

    // collection: restaurant
    {'_id': ObjectId('1'), 'name': 'green curry', 'owner': 'owner-20130411129'}

.. note::

    The option ``inverted_by`` only maps ``Owner.restaurant`` to ``Restaurant``
    virtually but the reference is stored in the **restaurant** collection.

One-to-many
-----------

.. warning::

    As there is no way to enforce relationships with built-in functionality of
    MongoDB and there will be constant checks for every write operation, it is
    not recommended to use unless it is for **reverse mapping** via the option
    ``inverted_by`` (see below for more information).

Many-to-one
-----------

(...)

Many-to-many
------------

(...)

Options for Associations
========================

(...)

.. seealso:: :doc:`../../api/db/index`
