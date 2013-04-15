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

.. note::

    As **lazy loading** is the heart of architectural design of the ORM,
    when an entity is mapped to an existing document, each property of
    the entity *in the clean state* will be a reference to either
    :class:`tori.db.common.ProxyObject`, which loads the data on demand for any
    **non-many-to-many mappings**, or :class:`tori.db.common.ProxyCollection`,
    which loads the list of proxy objects to the respective entities on demand
    only for any **many-to-many mappings**.

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
    from tori.db.mapper import link, AssociationType as t, CascadingType as c

Before getting started, here is the general table of abilities which will be
explained later on in this chapter.

+--------------------------+--------+----------------+---------------+
| Ability                  | Origin | Destination                    |
+                          +        +----------------+---------------+
|                          |        | Unidirectional | Bidirectional |
+==========================+========+================+===============+
| Map a property to object | Yes    | N/A            | Yes           |
+--------------------------+--------+----------------+---------------+
| Cascade opeations        | Yes    | N/A            | No, Ignored   |
+--------------------------+--------+----------------+---------------+
| Force read-only mode     | Yes    | N/A            | Yes           |
+--------------------------+--------+----------------+---------------+

where available operations are "merge", "delete", "persist", and "refresh".

One-to-one
----------

Suppose there are two entities: ``Owner`` and ``Restaurant``,
**one-to-one associations** imply the relationship between two entities as
described in the following UML::

     Owner (1) ----- (1) Restaurant

Unidirectional
~~~~~~~~~~~~~~

UML::

    Owner (1) <--x- (1) Restaurant

Suppose we have two classes: ``Owner`` and ``Restaurant``, where ``Restaurant``
has the one-to-one unidirectional relationship with ``Owner``.

.. code-block:: python

    @entity
    class Owner(object):
        def __init__(self, name):
            self.name  = name

    @link(
        target      = 'sampleapp.model.Owner',
        mapped_by   = 'owner',
        association = t.ONE_TO_ONE
    )
    @entity
    class Restaurant(object):
        def __init__(self, name, owner):
            self.name  = name
            self.owner = owner

where the sample of the stored documents will be:

.. code-block:: javascript

    // collection: owner
    {'_id': 'o-1', 'name': 'siamese'}

    // collection: restaurant
    {'_id': 'rest-1', 'name': 'green curry', 'owner': 'o-1'}

.. tip::

    To avoid the issue with the order of declaration, the full namespace in
    string is recommended to define the target class. However, the type
    reference can also be. For example, ``@link(target = Owner, ...)``.

Bidirectional
~~~~~~~~~~~~~

UML::

    Owner (1) <---> (1) Restaurant

Now, let's allow ``Owner`` to have a reference back to ``Restaurant`` where the
information about the reference is not kept with ``Owner``. So, the

.. code-block:: python

    @link(
        target      = 'sampleapp.model.Restaurant'
        inverted_by = 'owner',
        mapped_by   = 'restaurant',
        association = t.ONE_TO_ONE
    )
    @entity
    class Owner(object):
        def __init__(self, name, restaurant):
            self.name       = name
            self.restaurant = restaurant

where the the stored documents will be the same as the previous example.

``inverted_by`` means this class (``Owner``) maps ``Restaurant`` to the property
*restaurant* where the value of the property *owner* of the corresponding entity
of Restaurant must equal the *ID* of this class.

.. note::

    The option ``inverted_by`` only maps ``Owner.restaurant`` to ``Restaurant``
    virtually but the reference is stored in the **restaurant** collection.

Many-to-one
-----------

Suppose a ``Customer`` can have many ``Reward``'s as illustrated::

    Customer (1) ----- (0..n) Reward

Unidirectional
~~~~~~~~~~~~~~

UML::

    Customer (1) <--x- (0..n) Reward

.. code-block:: python

    @entity
    class Customer(object):
        def __init__(self, name):
            self.name    = name

    @link(
        target      = 'sampleapp.model.Customer',
        mapped_by   = 'customer',
        association = t.MANY_TO_ONE
    )
    @entity
    class Reward(object):
        def __init__(self, point, customer):
            self.point    = point
            self.customer = customer

where the data stored in the database can be like this:

.. code-block:: javascript

    // collection: customer
    {'_id': 'c-1', 'name': 'panda'}

    // collection: reward
    {'_id': 'rew-1', 'point': 2, 'customer': 'c-1'}
    {'_id': 'rew-2', 'point': 13, 'customer': 'c-1'}

.. _manual_orm_associations_m-1_bidirectional:

Bidirectional
~~~~~~~~~~~~~

UML::

    Customer (1) <---> (0..n) Reward

Just change ``Customer``.

.. code-block:: python

    @link(
        target      = 'sampleapp.model.Reward',
        inverted_by = 'customer',
        mapped_by   = 'rewards',
        association = t.ONE_TO_MANY
    )
    @entity
    class Customer(object):
        def __init__(self, name, rewards):
            self.name    = name
            self.rewards = rewards

where the property *rewards* refers to a list of rewards but the stored data
remains unchanged.

.. note:: This mapping is equivalent to a **bidirectional one-to-many mapping**.

One-to-many
-----------

Let's restart the example from the many-to-one section.

Unidirectional with Built-in List
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The one-to-many unidirectional mapping takes advantage of the built-in list.

UML::

    Customer (1) -x--> (0..n) Reward

.. code-block:: python

    @link(
        target      = 'sampleapp.model.Reward',
        mapped_by   = 'rewards',
        association = t.ONE_TO_MANY
    )
    @entity
    class Customer(object):
        def __init__(self, name, rewards):
            self.name    = name
            self.rewards = rewards

    @entity
    class Reward(object):
        def __init__(self, point):
            self.point = point

where the property ``rewards`` is a unsorted iterable list of ``Reward`` objects
and the data stored in the database can be like this:

.. code-block:: javascript

    // collection: customer
    {'_id': 'c-1', 'name': 'panda', 'reward': ['rew-1', 'rew-2']}

    // collection: reward
    {'_id': 'rew-1', 'point': 2}
    {'_id': 'rew-2', 'point': 13}

.. warning::

    As there is no way to enforce relationships with built-in functionality of
    MongoDB and there will be constant checks for every write operation, it is
    not recommended to use unless it is for **reverse mapping** via the option
    ``inverted_by`` (see below for more information).

    Without a proper checker, which is not provided for performance sake, this
    mapping can be used like the **many-to-many join-collection mapping**.

Bidirectional
~~~~~~~~~~~~~

See :ref:`Many-to-one Bidirectional Association <manual_orm_associations_m-1_bidirectional>`.

Many-to-many
------------

Suppose there are ``Teacher`` and ``Student`` where students can have many
teachers and vise versa::

    Teacher (*) ----- (*) Student

Similar other ORMs, the many-to-many mapping uses the corresponding join
collection.

Unidirectional with Join Collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UML::

    Teacher (*) <--x- (*) Student

.. code-block:: python

    @entity('teachers')
    class Teacher(object):
        def __init__(self, name):
            self.name = name

    @link(
        mapped_by   = 'teachers',
        target      = Teacher,
        association = AssociationType.MANY_TO_MANY,
        cascading   = [c.DELETE, c.PERSIST]
    )
    @entity('students')
    class Student(object):
        def __init__(self, name, teachers=[]):
            self.name     = name
            self.teachers = teachers

where the stored data can be like the following example:

.. code-block:: javascript

    // db.students.find()
    {'_id': 1, 'name': 'Shirou'}
    {'_id': 2, 'name': 'Shun'}
    {'_id': 3, 'name': 'Bob'}

    // db.teachers.find()
    {'_id': 1, 'name': 'John McCain'}
    {'_id': 2, 'name': 'Onizuka'}

    // db.students_teachers.find() // -> join collection
    {'_id': 1, 'origin': 1, 'destination': 1}
    {'_id': 2, 'origin': 1, 'destination': 2}
    {'_id': 3, 'origin': 2, 'destination': 2}
    {'_id': 4, 'origin': 3, 'destination': 1}

Bidirectional
~~~~~~~~~~~~~

Under development for Tori 2.1 (https://github.com/shiroyuki/Tori/issues/27).

Options for Associations
========================

The decorator :meth:`tori.db.mapper.link` has the following options:

=========== ============================================================================================
Option      Description
=========== ============================================================================================
association the type of associations (See :class:`tori.db.mapper.AssociationType`.)
cascading   the list of allowed cascading operations (See :class:`tori.db.mapper.CascadingType`.)
inverted_by the name of property used where **enable the reverse mapping if defined**
mapped_by   the name of property to be map
read_only   the flag to disable property setters (only usable with :class:`tori.db.common.ProxyObject`.)
target      the full name of class or the actual class
=========== ============================================================================================

.. seealso:: :doc:`../../api/db/index`
