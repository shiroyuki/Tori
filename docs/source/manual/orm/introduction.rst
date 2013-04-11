Introduction
************

The object-relational mapping (ORM) module in Tori is designed for non-relational
databases. The current version of ORM is designed only for MongoDB 2.2 or newer.
There are plans for other kinds of databases but there are not enough resources.

Definitions
===========

In this documentation, let's define:

:Entity:    Document
:Object ID: An primitive identifier (string, integer, or floating number) or an
            instance of :class:`bson.ObjectId`
:Pseudo ID: an instance of :class:`tori.db.common.PseudoObjectId`

Architecture
============

There are a few points to highlight.

* The lazy-loading strategy and proxy objects are used for loading data wherever
  applicable.
* The ORM uses **the unit-of-work pattern** as used by `Hibernate <http://www.hibernate.org/>`_
  in Java or `Doctrine <http://www.doctrine-project.org/>`_ in PHP.
* Although MongoDB does not has transaction support like MySQL, the ORM has
  sessions to manage the object graph within the same memory space.
* By containing a similar logic to determine whether a given entity is new or
  old, the following condition are used:

  * If a given entity is identified with an **object ID**, the given entity will
    be considered as an existing entity.
  * Otherwise, it will be a new entity.

* The object ID cannot be changed via the ORM interfaces.
* The ORM supports cascading operations on deleting, persisting, and refreshing.

Limitation
==========

* As **sessions** are not supported by MongoDB, the ORM cannot roll back in case
  that an exception are raisen or a writing operation is interrupted.
* Sessions cannot merge together. (Issue `#24 <https://github.com/shiroyuki/Tori/issues/24>`_
  by **spanote**)
* **Cascading operations on deleting** force the ORM to load the whole graph
  which potentially introduces performance issue on a large data set.
* **Cascading operations on persisting** force the ORM to load the data of all
  proxy objects but commiting changes will still be made only if there are changes.
* **Cascading operations on refreshing** force the ORM to reset the data and
  status of all entities, including proxy objects. However, the status of any
  entities marked for deletion will not be reset.
  