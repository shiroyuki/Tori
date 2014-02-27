Change Logs
###########

======= ==================================================================================
Code    Definition
======= ==================================================================================
BCB-x.y Backward-compatibility breakage caused by the marked features from version ``x.y``
======= ==================================================================================

Version 3.0
===========

- **ORM/tori.db**: (**BCB-2.1**) The setup of ORM becomes more generic in order to support multiple drivers.
- **ORM/tori.db**: (**BCB-2.1**) The query mechanism is changed to reduce the direct access to PyMongo APIs directly. It will be a **BCB** if the code that uses :class:'tori.db.criteria.Criteria' instantiates the class directly.
- **ORM/tori.db**: Removed unused / tedious code from the ORM.
- **Tests**: Reorganized the tests and refactored the ORM tests.