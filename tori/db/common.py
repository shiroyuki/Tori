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

        returnee       = {}
        relational_map = data.__relational_map__ if self._is_entity(data) else {}

        for name in dir(data):
            if name[0] == '_' or name == 'id':
                continue

            property_reference = data.__getattribute__(name)

            guide = relational_map[name] if name in relational_map else None

            if guide and guide.is_reverse_mapping:
                continue

            if callable(property_reference):
                continue

            if isinstance(property_reference, list):
                value = []

                for item in property_reference:
                    value.append(self._process_value(data, item, stack_depth))
            else:
                value = self._process_value(data, property_reference, stack_depth)

            returnee[name] = value

        if data.id and not isinstance(data.id, PseudoObjectId):
            returnee['_id'] = data.id

        return returnee

    def _is_entity(self, data):
        return '__relational_map__' in dir(data)

    def _process_value(self, data, value, stack_depth):
        is_proxy    = isinstance(value, ProxyObject)
        is_document = isinstance(data, object) and self._is_entity(data)

        processed_data = value

        if value and not self._is_primitive_type(value):
            if self._max_depth and stack_depth >= self._max_depth:
                processed_data = value
            elif is_proxy or is_document:
                processed_data = value.id
            else:
                processed_data = self.encode(value, stack_depth + 1)

        return processed_data

    def default_primitive_types(self):
        return super(Serializer, self).default_primitive_types() + [PseudoObjectId, ObjectId]

class PseudoObjectId(ObjectId):
    """Pseudo Object ID

    This class extends from :class:`bson.objectid.ObjectId`.
    """

    def __repr__(self):
        return "PseudoObjectId('%s')" % (str(self),)

class ProxyObject(object):
    def __init__(self, em, cls, object_id, read_only, cascading_options, is_reverse_proxy):
        self.__dict__['_collection'] = em.collection(cls)
        self.__dict__['_object_id']  = object_id
        self.__dict__['_object']     = None
        self.__dict__['_read_only']  = read_only
        self.__dict__['_cascading_options'] = cascading_options
        self.__dict__['_is_reverse_proxy']  = is_reverse_proxy

    def __getattr__(self, item):
        if not self.__dict__['_object']:
            entity = self._collection.get(self.__dict__['_object_id'])

            if entity:
                self.__dict__['_object'] = entity

        if item == '_actual':
            return self.__dict__['_object']
        elif item[0] == '_':
            return self.__dict__[item]
        elif not self.__dict__['_object_id'] or not self.__dict__['_object']:
            return None

        return self.__dict__['_object'].__getattribute__(item)

    def __setattr__(self, key, value):
        if self._read_only:
            raise ReadOnlyProxyException('The proxy is read only.')

        self._object.__setattr__(key, value)

class ProxyFactory(object):
    @staticmethod
    def make(session, id, mapping_guide):
        return ProxyObject(
            session,
            mapping_guide.target_class,
            id,
            mapping_guide.read_only,
            mapping_guide.cascading_options,
            mapping_guide.is_reverse_mapping
        )