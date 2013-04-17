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
        self.index_generated_on_the_fly = False

    def build_cursor(self, repository):
        api    = repository.api
        cursor = api.find(self.condition)

        try:
            if self.order_by:
                cursor.sort(self.order_by)
        except TypeError as exception:
            # If it fails to tell the cursor to sort the result, automatically
            # generate the corresponding index.
            if self.index_generated_on_the_fly:
                return []

            self.index_generated_on_the_fly = True

            api.create_index([
                (name, self.order_by[name]) for name in self.order_by
            ])

            return self.build_cursor(repository)

        if self.offset and self.offset > 0:
            cursor.skip(self.offset)

        if self.limit and self.limit > 0:
            cursor.limit(self.limit)

        return cursor