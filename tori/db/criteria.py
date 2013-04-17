from imagination.decorator.validator import restrict_type

class Order(object):
    """ Sorting Order Definition """
    ASC  = 1
    """ Ascending Order """
    DESC = -1
    """ Descending Order """

class Criteria(object):
    """ Criteria
    """
    @restrict_type(condition=dict, order_by=dict, offset=int, limit=int)
    def __init__(self, condition={}, order_by={}, offset=0, limit=0):
        self.condition = condition
        self.order_by  = order_by
        self.offset    = offset
        self.limit     = limit

    def build_cursor(self, repository):
        api    = repository.api
        cursor = api.find(self.condition)

        if self.order_by:
            cursor.sort(self.order_by)

        if self.offset and self.offset > 0:
            cursor.skip(self.offset)

        if self.limit and self.limit > 0:
            cursor.limit(self.limit)

        return cursor