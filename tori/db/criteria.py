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
from tori.db.expression import Criteria

class Order(object):
    """ Sorting Order Definition """
    ASC  = pymongo.ASCENDING
    """ Ascending Order """
    DESC = pymongo.DESCENDING
    """ Descending Order """

class Query(object):
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
        self._criteria = None
        self._join_map   = {}
        self._definition_map  = {}

    @property
    def is_new_style(self):
        return bool(self.criteria)

    @property
    def definition_map(self):
        return self._definition_map

    @definition_map.setter
    def definition_map(self, value):
        self._definition_map = value

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
    def criteria(self):
        """ Expression Criteria """
        return self._criteria

    @criteria.setter
    def criteria(self, value):
        expected_type = Criteria

        if not isinstance(value, expected_type):
            raise ValueError('The {} object should be given, not {}.'.format(expected_type.__name__, type(value).__name__))

        self._criteria = value

    @property
    def join_map(self):
        """ A join map """
        return self._join_map

    @join_map.setter
    def join_map(self, value):
        self._join_map = value

    def join(self, property_path, alias):
        """ Define a join path """
        if not (alias != self.alias and alias not in self._join_map):
            raise KeyError('The alias of the joined entity must be unique.')

        self._join_map[alias] = {
            'path':   property_path,
            'class':  None,
            'mapper': None
        }

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

    def new_criteria(self):
        """ Get a new expression for this criteria

            :rtype: tori.db.expression.Criteria
        """
        return Criteria()

    def expect(self, statement):
        """ Define the condition / expectation of the main expression.

            :param statement: the conditional statement
            :type  statement: str

            This is a shortcut expression to define expectation of the main
            expression. The main expression will be defined automatically
            if it is undefined. For example,

            .. code-block:: python

                c = Query()
                c.expect('foo = 123')

            is the same thing as

            .. code-block:: python

                c = Query()
                c.criteria = c.new_criteria()
                c.criteria.expect('foo = 123')
        """
        if not self.criteria:
            self.criteria = self.new_criteria()

        self.criteria.expect(statement)

    def define(self, variable_name=None, value=None, **definition_map):
        """ Define the value of one or more variables (known as parameters).

            :param variable_name: the name of the variable (for single assignment)
            :type  variable_name: str
            :param value: the value of the variable (for single assignment)
            :param definition_map: the variable-to-value dictionary

            This method is usually recommended be used to define multiple variables
            like the following example.

            .. code-block:: python

                criteria.define(foo = 'foo', bar = 2)

            However, it is designed to support the assign of a single user. For
            instance,

            .. code-block:: python


        """
        is_single_definition = bool(variable_name and value)
        is_batch_definition  = bool(definition_map)

        if is_single_definition and not is_batch_definition:
            self.definition_map[variable_name] = value

            return
        elif not is_single_definition and is_batch_definition:
            self.definition_map.update(definition_map)

            return

        raise ValueError('Cannot define one variable or multiple variables at the same time.')

    def reset_definitions(self):
        self.definition_map = {}

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