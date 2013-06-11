Cascading
*********

This is the one toughest section to write.

MongoDB, as far as everyone knows, does not support cascading operations like
the way MySQL and other vendors do with cascading deletion. Nevertheless, Tori
supports cascading through the database abstraction layer (DBAL).

.. warning::

    Cascading persistence and removal via DBAL has high probability of degrading
    performance with large dataset as in order to calculate a dependency graph,
    all data must be loaded into the memory space of the computing process. This
    introduces a spike in memory and network usage.

    This feature is introduced for convenience sake but should be used sparingly
    or accounted for potential performance degration.

Here is a sample scenario.

Suppose I have two types of objects: a sport team and a player. When a team is
updated, removed or refreshed, the associated player should be treated the same
way as the team. Here is a sample code.

.. code-block:: python

    from tori.db.entity import entity
    from tori.db.mapper import CascadingType as c

    @entity
    class Player(object):
        pass # omit the usual setup decribed in the basic usage.

    @link(
        target=Player,
        mapped_by='player',
        cascading=[c.PERSIST, c.DELETE, c.REFRESH]
    )
    @entity
    class Team(object):
        pass # omit the usual setup decribed in the basic usage.

Now, whatever operation is used on a Team entity, associated Player entites are
subject to the same operation.