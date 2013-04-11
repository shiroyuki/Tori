Handling transaction
********************

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