"""
Common Module
=============

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Stability: Stable
"""

from time import time
from bson import ObjectId

from tori.common import Enigma
from tori.data.serializer import ArraySerializer

class Serializer(ArraySerializer):
    def encode(self, data, stack_depth=0):
        if not isinstance(data, object):
            raise TypeError('The provided data must be an object')

        returnee = {}

        for name in dir(data):
            if name[0] == '_' or name == 'id':
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

        if data.id and not isinstance(data.id, PseudoObjectId):
            returnee['_id'] = data.id

        return returnee

    def default_primitive_types(self):
        return super(Serializer, self).default_primitive_types() + [PseudoObjectId]

class GuidGenerator(object):
    """Simply GUID Generator"""
    def __init__(self):
        self.counter     = 0
        self.known_guids = []

    def generate(self):
        """Generate the GUID

        :return: Global unique identifier within the scope of the generator
        :rtype: str
        """
        self.counter = self.counter + 1

        guid = None

        while guid in self.known_guids or not guid:
            guid = self._generate()

        return guid

    def _generate(self):
        """Generate an identifier

        :return: Global unique identifier within the scope of the generator
        :rtype: str
        """
        return u'{}.{}'.format(time(), self.counter)

class HashGuidGenerator(GuidGenerator):
    """Hash-type GUID Generator"""

    def __init__(self):
        GuidGenerator.__init__(self)

        self.enigma = Enigma.instance()

    def _generate(self):
        return self.enigma.hash(super(self, GuidGenerator)._generate())

class PseudoObjectId(ObjectId):
    """Pseudo Object ID

    This class extends from :class:`bson.objectid.ObjectId`.
    """