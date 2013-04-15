Handling transactions (sessions)
********************************

Similar to `Sessions in SQLAlchemy <http://docs.sqlalchemy.org/en/latest/orm/session.html>`_.

In the most general sense, the session establishes all conversations with the
database and represents a “holding zone” for all the objects which you’ve loaded
or associated with it during its lifespan. It provides the entrypoint to acquire
a :class:`tori.db.orm.repository.Repository` object, which sends queries to the
database using the current database connection of the session (:class:`tori.db.orm.session.Session`),
populating result rows into objects that are then stored in the session, inside
a structure called the identity map (internally being the combination of "the
record map" and "the object ID map") - a data structure that maintains unique
copies of each object, where “unique” means “only one object with a particular
primary key”.

The session begins in an essentially stateless form. Once queries are issued or
other objects are persisted with it, it requests a connection resource from an
manager that is associated with the session itself. This connection represents
an ongoing transaction, which remains in effect until the session is instructed
to commit.

All changes to objects maintained by a session are tracked - before the database
is queried again or before the current transaction is committed, it flushes all
pending changes to the database. This is known as **the Unit of Work pattern**.

When using a session, it’s important to note that the objects which are associated
with it are **proxy objects** (:class:`tori.db.orm.common.ProxyObject`) to the
transaction being held by the session - there are a variety of events that will
cause objects to re-access the database in order to keep synchronized. It is
possible to “detach” objects from a session, and to continue using them, though
this practice has its caveats. It’s intended that usually, you’d re-associate
detached objects with another Session when you want to work with them again, so
that they can resume their normal task of representing database state.

Supported Operations
====================

=================== =================
Supported Operation Supported Version
=================== =================
Persist             2.1
Delete              2.1
Refresh             2.1
Merge               Planned for 2014
Detach              Planned for 2014
=================== =================

Example
=======

First, define the entity manager.

.. code-block:: python

    from pymongo             import Connection
    from tori.db.orm.manager import Manager
    
    connection     = Connection()
    entity_manager = Manager('default', connection)

.. tip::

    Alternatively, you can write just ``entity_manager = Manager('default')``
    where the manager will use the default settings of ``Connection``, which
    is for **localhost** on the default port.

Then, open a session::

    session = entity_manager.open_session()

Then, try to query for "Bob" (``User``) with :class:`tori.db.orm.repository.Repository`::

    bob = session.collection(User).filter_one({'name', 'Bob'})
    print(bob.address)

The output should show::

    Bangkok, Thailand

Then, update his address::

    bob.address = 'London, UK'
    session.persist(bob)

Or, delete ``bob``::

    session.delete(bob)

Or, refresh ``bob``::

    session.refresh(bob)

Then, if ``bob`` is either **persisted** or **deleted**, to flush/commit the
change, simply run::

    session.flush(bob)

Drawbacks Introduced by Either MongoDB or Tori
==============================================

#. Even though MongoDB does not support transactions, like some relational database
   engines, such as, InnoDB, Tori provides software-based transactions. However,
   as mentioned earlier, Tori **does not provide roll-back operations**.
#. **Merging** and **detaching** operations are currently not supported in 2013
   unless someone provides the supporting code.
#. Any querying operations cannot find any uncommitted changes.
