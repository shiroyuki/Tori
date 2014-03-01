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
* The ORM uses **the Unit Of Work pattern** as used by:

  * `Hibernate <http://www.hibernate.org/>`_ (Java)
  * `Doctrine <http://www.doctrine-project.org/>`_ (PHP)
  * `SQLAlchemy <http://www.sqlalchemy.org/>`_ (Python)

* Although MongoDB does not has transaction support like MySQL, the ORM has
  sessions to manage the object graph within the same memory space.
* By containing a similar logic to determine whether a given entity is new or
  old, the following condition are used:

  * If a given entity is identified with an **object ID**, the given entity will
    be considered as an existing entity.
  * Otherwise, it will be a new entity.

* The object ID cannot be changed via the ORM interfaces.
* The ORM supports cascading operations on deleting, persisting, and refreshing.
* Heavily rely on **public properties**, which does not have leading underscores
  (``_``) to map between class properties and document keys, except the property
  **id** will be converted to the key **_id**.

Limitation
==========

* As **sessions** are not supported by MongoDB, the ORM cannot roll back in case
  that an exception are raisen or a writing operation is interrupted.
* Sessions cannot merge together.
* **Cascading operations on deleting** forces the ORM to load the whole graph
  which potentially introduces performance issue on a large data set.
* **Cascading operations on persisting** force the ORM to load the data of all
  proxy objects but commiting changes will still be made only if there are changes.
* **Cascading operations on refreshing** force the ORM to reset the data and
  status of all entities, including proxy objects. However, the status of any
  entities marked for deletion will not be reset.
* Some database operations are not supported or optimized due to the non-generalized
  interfaces as shown on the table in the next section. (Introduced in Tori 3.0)
* **LevelDB** will only be supported for **Python 2.7** as the underlying library
  `leveldb <https://code.google.com/p/py-leveldb/>`_ only supports Python 2.7 due
  to its dependency.

Supported SQL-equivalent Querying Operations
============================================

.. versionadded:: 3.0

=============================== ============ ========= ========= ======= =====
SQL-equivalent Operation        MongoDB 2.4+ Riak 1.4+ Riak 2.0+ LevelDB Redis
=============================== ============ ========= ========= ======= =====
CRUD operations                 Yes          Yes       Yes       Yes     Yes
Simple query                    Yes          No        Unknown   No      No
AND compound statement          Yes          No        Unknown   No      No
OR compound statement           Unknown      No        Unknown   No      No
Filter with regular expression  Yes          No        Unknown   No      No
Range filter                    Yes          No        Unknown   No      No
Query optimization with index   Yes          Yes       Yes       No      No
Directly use indice for query   No           Yes       Yes       No      No
Store the data as they are\*    Yes          Yes       Yes       No      No
=============================== ============ ========= ========= ======= =====

.. note::

    Some databases may store a complex-structured data, which is always the case
    when the ORM stores the structured data of the entity.