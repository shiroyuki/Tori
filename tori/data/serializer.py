from tori.decorator.common import singleton

@singleton
class ArraySerializer(object):
    def __init__(self, max_depth=2):
        self._max_depth = max_depth
        self._primitive_types = []

    def set_max_depth(self, max_depth):
        self._max_depth = max_depth

    def encode(self, data, stack_depth=0):
        if not isinstance(data, object):
            raise TypeError('The provided data must be an object')

        returnee = {}

        for name in dir(data):
            if name[0] == '_':
                continue

            value = data.__getattribute__(name)

            if callable(value):
                continue

            if value and not self._is_primitive_type(value):
                if self._max_depth and stack_depth >= self._max_depth:
                    value = u'%s' % value
                else:
                    value = self.encode(value, stack_depth + 1)

            returnee[name] = value

        return returnee

    def _is_primitive_type(self, value):
        if not self._primitive_types:
            self._primitive_types = self.default_primitive_types()

        return type(value) in self._primitive_types

    def default_primitive_types(self):
        try:
            return [int, float, str, list, dict, tuple, set, bool, unicode, long]
        except NameError as exception:
            return [int, float, str, list, dict, tuple, set, bool]