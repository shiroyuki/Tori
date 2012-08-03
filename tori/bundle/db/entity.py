'''
:Author: Juti Noppornpitak

Relational Database Entity

This module just provides :class:`tori.rdb.Entity` as a result of the factory method
:meth:`sqlalchemy.ext.declarative.declarative_base`.  

'''

from sqlalchemy.ext.declarative import declarative_base

Entity = declarative_base()