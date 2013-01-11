Concept and Philosophy
**********************

Tori Framework is designed to incorporates:

* the adapted version of :pep:`8` with Object Calisthenics
* **the aspect-oriented programming pattern**
* **the dependency injection pattern**

altogether. Despite of that, there are a few irregular things: the controller-repository-model pattern, standalone
sub-modules and non-circular dependency graph.

Controller-Repository-Model Pattern (CRM)
=========================================

If a sub module has to deal with static or indexed data, the controller-repository-model pattern (CRM) will be used
where:

* **controllers** are front-end interfaces used to provide data in the general way
* **repositories** are back-end interfaces used to access data specifically for a particular type of data
* **models** or **entities** are models representing the data retrieved by the repositories and known by the controllers.

For instance, the session module has :class:`tori.session.controller.Controller` as the only controller, any classes in
:py:mod:`tori.session.repository` as a repository and any classes in :py:mod:`tori.session.entity` as an entity (or
data structure) if required by the repository.

Standalone Sub-modules
======================

Some sub-modules are designed to work independently without the need of other sub-modules. This only applies to
low-level modules like navigation (:py:mod:`tori.navigation`), ORM (:py:mod:`tori.db`) and templating module (:py:mod:`tori.template`).

Non-circular Dependency Graph
=============================

All modules in Tori Framework have unidirectional relationship at the module and code level. The reasons beside all of
other cool reasons, many of which you may have heard somewhere else, of doing this is for easy maintenance, easy testing
and infinite-loop prevention.