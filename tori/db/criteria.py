"""
:mod:`tori.db.criteria` -- Query Criteria
=========================================

.. module:: tori.db.criteria
   :platform: All
   :synopsis: The metadata for querying data from the backend data storage
.. moduleauthor:: Juti Noppornpitak <jnopporn@shiroyuki.com>
"""

import pymongo
from imagination.decorator.validator import restrict_type
from tori.db.expression import Expression

class Order(object):
    """ Sorting Order Definition """
    ASC  = pymongo.ASCENDING
    """ Ascending Order """
    DESC = pymongo.DESCENDING
    """ Descending Order """

class Criteria(object):
    """ Criteria

        .. note::

            The current implementation does not support filtering on
            associated entities.

    """
    def __init__(self, alias):
        self._alias     = alias
        self._condition = {}
        self._origin    = None # str - the name of the collection / repository
        self._order_by  = []
        self._offset    = 0
        self._limit     = 0
        self._indexed   = False
        self._force_loading = False
        self._auto_index    = False
        self._indexed_target_list = []
        self._expression = None

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, value):
        self._alias = value

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, value):
        assert isinstance(value, Expression), 'The Expression object should be given, not {}.'.format(type(value))
        self._expression = value

    def where(self, key_or_full_condition, filter_data=None):
        """ Define the condition

            .. deprecated:: 3.1

                Starting in Tori 3.0, the new way to query will be.

            :type  key_or_full_condition: str or dict
            :param key_or_full_condition: either the key of the condition
                                          (e.g., a field name, $or, $gt etc.)
            :param filter_data: the filter data associating to the key
        """
        if isinstance(key_or_full_condition, dict):
            if filter_data:
                raise ValueError('Assuming that the full condition is given, the looking value is not required.')

            self._condition = key_or_full_condition

            return self

        # if this is not a special instruction, append for indexing.
        if key_or_full_condition[0] != '$':
            self._indexed_target_list.append(key_or_full_condition)

        self._condition[key_or_full_condition] = filter_data

        return self

    def order(self, field, direction=Order.ASC):
        """ Define the returning order

            :param field: the sorting field
            :type  field: str
            :param direction: the sorting direction
        """
        if field == 'id':
            field = '_id'

        self._order_by.append((field, direction))

        return self

    def start(self, offset):
        """ Define the filter offset

            :param offset: the filter offset
            :type  offset: int
        """
        self._offset = offset

        return self

    def limit(self, limit):
        """ Define the filter limit

            :param limit: the filter limit
            :type  limit: int
        """
        self._limit = limit

        return self

    def force_loading(self, flag):
        self._force_loading = flag

        return self

    def auto_index(self, flag):
        self._auto_index = flag

        return self

    def new_expression(self):
        return Expression()

    def __str__(self):
        statements = []

        if self._condition:
            statements.append('WHERE ' + str(self._condition))

        if self._order_by:
            statements.append('ORDER BY ' + str(self._order_by))

        if self._offset:
            statements.append('OFFSET ' + str(self._offset))

        if self._limit:
            statements.append('LIMIT ' + str(self._limit))

        return ' '.join(statements)