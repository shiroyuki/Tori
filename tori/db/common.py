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
from tori.db.exception import ReadOnlyProxyException

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
                elif isinstance(value, ProxyObject):
                    value = ProxyObject.id
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

class ProxyObject(object):
    def __init__(self, em, cls, object_id, read_only, cascading_options):
        self._collection = em.collection(cls)
        self._object_id  = object_id
        self._object     = None
        self._read_only  = read_only
        self._cascading_options = cascading_options

    def __getattr__(self, item):
        if not self._object:
            self._object = self._collection.get(self._object_id)

        if item == '_actual':
            return self._object
        elif item[0] == '_':
            return self.__getattribute__(item)

        return self._object.__getattribute__(item)

    def __setattribute__(self, key, value):
        if self._read_only:
            raise ReadOnlyProxyException('The proxy is read only.')

        if not self._object:
            self._object = self._collection.get(self._object_id)

        self._object.__setattr__(key, value)