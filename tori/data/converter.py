from tori.decorator.common import singleton

@singleton
class ArrayConverter(object):
    def __init__(self):
        self._max_depth = 2
        self._permitive_types = []

    def set_max_depth(self, max_depth):
        self._max_depth = max_depth

    def convert(self, data, stack_depth=0):
        if not isinstance(data, object):
            raise TypeError('The provided data must be an object');

        returnee = {}

        for name in dir(data):
            if name[0] == '_':
                continue

            value = data.__getattribute__(name)

            if callable(value):
                continue

            if not self._is_pirmitive_type(value):
                if self._max_depth and stack_depth >= self._max_depth:
                    value = u'%s' % value
                else:
                    value = self.convert(value, stack_depth + 1)

            returnee[name] = value

        return returnee

    def _is_pirmitive_type(self, value):
        if not self._permitive_types:
            self._permitive_types = [int, float, str, list, dict, tuple, set, bool]

            # Prevent the code from raising exceptions due to Python-3 backward-compatibility break.
            try:
                self._permitive_types.extend([unicode, long])
            except:
                pass

        return type(value) in self._permitive_types