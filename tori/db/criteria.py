import pymongo
from imagination.decorator.validator import restrict_type

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
    def __init__(self):
        self._condition = {}
        self._order_by  = []
        self._offset    = 0
        self._limit     = 0
        self._indexed   = False
        self._indexed_target_list = []

    def where(self, key_or_full_condition, filter_data=None):
        """ Define the condition

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

    def build_cursor(self, repository, force_loading=False, auto_index=False):
        """ Build the cursor

            :param repository: the repository
            :type  repository: tori.db.repository.Repository
            :param force_loading: force loading on any returned entities
            :type  force_loading: bool
            :param auto_index: the flag to automatically index sorting fields
            :type  auto_index: bool

            .. note:: This is mainly used by a repository internally.
        """
        api    = repository.session.driver
        cursor = api.find(repository.name, self._condition)

        if not force_loading and self._limit != 1:
            cursor = api.find(repository.name, self._condition, fields=[])

        if auto_index and not self._indexed:
            if self._indexed_target_list:
                for field in self._indexed_target_list:
                    repository.index(field)

            if auto_index and not self._indexed:
                repository.index(self._order_by)

            self._indexed = True

        if self._order_by:
            cursor.sort(self._order_by)

        if self._offset and self._offset > 0:
            cursor.skip(self._offset)

        if self._limit and self._limit > 0:
            cursor.limit(self._limit)

        return cursor

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