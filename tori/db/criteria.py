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
    """
    @restrict_type(condition=dict, order_by=dict, offset=int, limit=int)
    def __init__(self, condition={}, order_by={}, offset=0, limit=0, force_loaded=False):
        self.condition = condition
        self.order_by  = order_by
        self.offset    = offset
        self.limit     = limit
        self.index_generated_on_the_fly = False

    def build_cursor(self, repository, force_loading=False):
        api    = repository.api
        cursor = api.find(self.condition)

        if not force_loading and self.limit != 1:
            cursor = api.find(self.condition, fields=[])

        try:
            if self.order_by:
                cursor.sort(self.ordering_sequence)
        except TypeError as exception:
            # If it fails to tell the cursor to sort the result, automatically
            # generate the corresponding index.
            if self.index_generated_on_the_fly:
                api.create_index(self.ordering_sequence)

            self.index_generated_on_the_fly = True

            return self.build_cursor(repository)

        if self.offset and self.offset > 0:
            cursor.skip(self.offset)

        if self.limit and self.limit > 0:
            cursor.limit(self.limit)

        return cursor

    @property
    def ordering_sequence(self):
        return [
            (name, self.order_by[name]) for name in self.order_by
        ]

    def __str__(self):
        statements = []

        if self.condition:
            statements.append('WHERE ' + str(self.condition))

        if self.order_by:
            statements.append('ORDER BY ' + str(self.order_by))

        if self.offset:
            statements.append('OFFSET ' + str(self.offset))

        if self.limit:
            statements.append('LIMIT ' + str(self.limit))

        return ' '.join(statements)