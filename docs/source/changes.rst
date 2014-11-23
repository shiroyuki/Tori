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

- [Planned] Possibly removed ``tori.db.session.Session.register_class(...)``.
- [Planned] Switch from **tori.db** to **Passerine ORM**.

Version 3.0
===========

:Release Date: 2014.11.23

.. note::

    **tori.db** has been spinned off as project **Passerine ORM**
    (https://github.com/shiroyuki/passerine). Tori 3.0 only contains
    the testing version of **Passerine ORM**. The documentation for
    **Passerine** (http://passerine-orm.readthedocs.org/) is compatible
    with **tori.db**.

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
- **Web Framework**: (**BCB-2.1**) The **simple routing scheme** is now default instead of the **regular expression** originally used by Tornado. (The router class will take care of the translation.)
- **Web Framework**: The first instance of :class:`tori.application.Application` is now self-referenced as ``tori.centre.core``.
- **Web Framework**: Add a file-base session repository. This allows the app to store the session data as a json file.
- **Web Framework**: Without specifying the rendering path for each controller, the controller will be looking for
  templates from :file:`<app_base_path>/templates`.
- **Web Framework**: Introduce :doc:`/manual/configuration/predefined-config.rst`. (The old style will be deprecated in 3.2.)
- **Tests**: Reorganized the tests and refactored the ORM tests.
