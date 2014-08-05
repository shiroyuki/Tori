Change Logs
###########

======= ==================================================================================
Code    Definition
======= ==================================================================================
BCB-x.y Backward-compatibility breakage caused by the marked features from version ``x.y``
======= ==================================================================================

Version 3.1
===========

:Release Date: TBA

- Possibly removed ``tori.db.session.Session.register_class(...)``.

Version 3.0
===========

:Release Date: 2014.08.16

- **ORM/tori.db**: Allow cross-collection (or cross-repository) queries within the same type of backend datastores.
- **ORM/tori.db**: (**BCB-2.1**) Removed the silly preconditions of the setup of ORM.
- **ORM/tori.db**: (**BCB-2.1**) The setup of ORM becomes more generic in order to support multiple drivers.
- **ORM/tori.db**: (**BCB-2.1**) No auto indexing.
- **ORM/tori.db**: (**BCB-2.1**) The query mechanism is changed to reduce the direct access to PyMongo APIs directly. It
  will be a **BCB** if the code that uses :class:`tori.db.criteria.Criteria` instantiates the class directly.
- **ORM/tori.db**: (**BCB-2.1**) Class **Criteria** has been renamed to **Query** as the internal class will be labeled
  as **Criteria**. This change is to address the semantic / readability issue. (Hence, all references to Criteria objects
  are now referred to Query objects.)
- **ORM/tori.db**: Removed unused / tedious code from the ORM.
- **Web Framework**: The first instance of :class:`tori.application.Application` is now self-referenced as ``tori.centre.core``.
- **Web Framework**: Without specifying the rendering path for each controller, the controller will be looking for
  templates from :file:`<app_base_path>/templates`.
- **Web Framework**: Introduce the new-style configuration which is a JSON file. (The old style will be deprecated in 3.2.)
- **Web Framework**
- **Tests**: Reorganized the tests and refactored the ORM tests.

New Style Configuration
-----------------------

In 3.0, it is required to specify in the configuration in order to use the new style configuration where the default
configuration tree is:

.. code-block:: javascript

    {
        "session": {
            "class": "tori.session.repository.memory.Memory"
            "params": {}
        }
        "db": {
            "managers": {}
        }
    }

where ``db.managers`` is mapping a alias of the manager to a corresponding DB URL only referred by the database manager factory.

For example, we have :file:`config.json`.

.. code-block:: javascript

    {
        "db": {
            "managers": {
                "db.directory": "mongodb://localhost/directory"
            }
        }
    }

Add this line to the XML configuration file.

.. code-block:: xml

    <use src="config.json"/>

