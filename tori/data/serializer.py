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

            # Prevent the code from raising exceptions due to Python-3 backward-compatibility break.
            try:
                self._permitive_types.extend([unicode, long])
            except:
                pass

        return type(value) in self._primitive_types

    def default_primitive_types(self):
        return [int, float, str, list, dict, tuple, set, bool]