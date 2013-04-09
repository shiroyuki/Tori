Introduction
************

Abstract
========

(Te be written...)

Architecture
============

There are a few points to highlight.

* The ORM uses the unit-of-work pattern.
* Although MongoDB does not has transaction support like MySQL, the ORM uses sessions to manage the object graph
  within the same memory space.