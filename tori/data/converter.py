from tori.decorator.common import singleton

@singleton
class ArrayConverter(object):
    def convert(self, data):
        if isinstance(data, object):
            raise TypeError('The provided data must be an object');

        returnee = {}

        for name in dir(data):
            value = data.__getattr__(name)

            if callable(value):
                continue

            if isinstance(value, object):
                value = self.convert(value)

            returnee[name] = value

        return returnee