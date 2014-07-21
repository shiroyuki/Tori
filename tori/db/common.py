# -*- coding: utf-8 -*-
"""
:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Stability: Stable
"""

from bson import ObjectId

from tori.data.serializer import ArraySerializer
from tori.db.exception import ReadOnlyProxyException
from tori.db.metadata.helper import EntityMetadataHelper

class Serializer(ArraySerializer):
    """ Object Serializer for Entity
    """
    def extra_associations(self, data, stack_depth=0):
        if not isinstance(data, object):
            raise TypeError('The provided data must be an object')

        returnee           = {}
        relational_map     = EntityMetadataHelper.extract(data).relational_map if self._is_entity(data) else {}
        extra_associations = {}

        for name in dir(data):
            # Skip all protected/private/reserved properties.
            if self._is_preserved_property(name):
                continue

            guide = self._retrieve_guide(relational_map, name)

            # Skip all properties without an associative guide or with reverse mapping or without pseudo association class.
            if not guide or guide.inverted_by or not guide.association_class:
                continue

            property_reference = data.__getattribute__(name)

            # Skip all callable properties and non-list properties
            if callable(property_reference) or not isinstance(property_reference, list):
                continue

            # With a valid association class, this property has the many-to-many relationship with the other entity.
            extra_associations[name] = []

            for destination in property_reference:
                extra_associations[name].append(destination.id)

        return extra_associations

    def encode(self, data, stack_depth=0, convert_object_id_to_str=False):
        """ Encode data into dictionary and list.

            :param data:        the data to encode
            :param stack_depth: traversal depth limit
            :param convert_object_id_to_str: flag to convert object ID into string
        """
        if not isinstance(data, object):
            raise TypeError('The provided data must be an object')

        returnee       = {}
        relational_map = EntityMetadataHelper.extract(data).relational_map if self._is_entity(data) else {}

        for name in dir(data):
            # Skip all protected/private/reserved properties.
            if self._is_preserved_property(name):
                continue

            guide = self._retrieve_guide(relational_map, name)

            # Skip all pseudo properties used for reverse mapping.
            if guide and guide.inverted_by:
                continue

            property_reference = data.__getattribute__(name)

            is_list = isinstance(property_reference, list)
            value   = None

            # Skip all callable properties
            if callable(property_reference):
                continue

            # For one-to-many relationship, this property relies on the built-in list type.
            if is_list:
                value = []

                for item in property_reference:
                    value.append(self._process_value(data, item, stack_depth, convert_object_id_to_str))
            else:
                value = self._process_value(data, property_reference, stack_depth, convert_object_id_to_str)

            returnee[name] = value

        # If this is not a pseudo object ID, add the reserved key '_id' with the property 'id' .
        if data.id and not isinstance(data.id, PseudoObjectId):
            returnee['_id'] = self._process_value(data, data, stack_depth, convert_object_id_to_str)

        return returnee

    def _retrieve_guide(self, relational_map, name):
        return relational_map[name] if name in relational_map else None

    def _is_preserved_property(self, name):
        return name[0] == '_' or name == 'id'

    def _is_entity(self, data):
        return EntityMetadataHelper.hasMetadata(data)

    def _process_value(self, data, value, stack_depth, convert_object_id_to_str):
        is_proxy    = isinstance(value, ProxyObject)
        is_document = isinstance(data, object) and self._is_entity(data)

        processed_data = value

        if value and not self._is_primitive_type(value):
            if self._max_depth and stack_depth >= self._max_depth:
                processed_data = value.encode('utf-8', 'replace') if self._is_string(value) else value
            elif is_proxy or is_document:
                processed_data = value.id

                if isinstance(processed_data, ObjectId) and convert_object_id_to_str:
                    processed_data = str(processed_data)
            else:
                processed_data = self.encode(value, stack_depth + 1)
        elif isinstance(value, ObjectId) and convert_object_id_to_str:
            processed_data = str(value)

        return processed_data

    def default_primitive_types(self):
        return super(Serializer, self).default_primitive_types() + [PseudoObjectId, ObjectId]

class PseudoObjectId(ObjectId):
    """ Pseudo Object ID

        This class extends from :class:`bson.objectid.ObjectId`.

        This is used to differentiate stored entities and new entities.
    """

    def __str__(self):
        return 'P-{}'.format(super(PseudoObjectId, self).__str__())

    def __repr__(self):
        return "PseudoObjectId('%s')" % (str(self),)

class ProxyObject(object):
    """ Proxy Collection

        This class is designed to only load the entity whenever the data access
        is required.

        :param session: the managed session
        :type  session: tori.db.session.Session
        :param cls: the class to map the data
        :type  cls: type
        :param object_id: the object ID
        :param read_only: the read-only flag
        :type  read_only: bool
        :param cascading_options: the cascading options
        :type  cascading_options: list or tuple
        :param is_reverse_proxy: the reverse proxy flag
        :type  is_reverse_proxy: bool
    """
    def __init__(self, session, cls, object_id, read_only, cascading_options, is_reverse_proxy):
        if isinstance(cls, ProxyObject) or not object_id:
            raise RuntimeError('Cannot initiate a proxy')

        self.__dict__['_class']      = cls
        self.__dict__['_collection'] = session.collection(cls)
        self.__dict__['_object_id']  = object_id
        self.__dict__['_object']     = None
        self.__dict__['_read_only']  = read_only
        self.__dict__['_cascading_options'] = cascading_options
        self.__dict__['_is_reverse_proxy']  = is_reverse_proxy

    def __get_object(self):
        if not self.__dict__['_object_id']:
            raise RuntimeError('Cannot load the proxy')

        if not self.__dict__['_object']:
            entity = self._collection.get(self.__dict__['_object_id'])

            if entity:
                self.__dict__['_object'] = entity

        return self.__dict__['_object']

    def __getattr__(self, item):
        if item == '_actual':
            return self.__get_object()
        #elif item == 'id':
        #    return self.__dict__['_object_id']
        elif item[0] == '_':
            return self.__dict__[item]
        elif not self.__dict__['_object_id'] or not self.__get_object():
            return None

        return self.__get_object().__getattribute__(item)

    def __setattr__(self, key, value):
        if self._read_only:
            raise ReadOnlyProxyException('The proxy is read only.')

        self.__get_object().__setattr__(key, value)

class ProxyCollection(list):
    """ Proxy Collection

        This collection is extended from the built-in class :class:`list`,
        designed to only load the associated data whenever is required.

        :param session: the managed session
        :type  session: tori.db.session.Session
        :param origin: the origin of the association
        :type  origin: object
        :param guide: the relational guide
        :type  guide: tori.db.mapper.RelatingGuide

        .. note:: To replace with criteria and driver
    """
    def __init__(self, session, origin, guide):
        self._session = session
        self._origin  = origin
        self._guide   = guide
        self._loaded  = False

    def reload(self):
        """ Reload the data list

            .. warning::

                This method is **not recommended** to be called directly. Use
                :meth:`tori.db.session.Session.refresh` on the owned object
                instead.
        """
        while len(self):
            self.pop(0)

        self._loaded = False

        self._prepare_list()

    def _prepare_list(self):
        if self._loaded:
            return

        self._loaded = True

        association_class = self._guide.association_class.cls
        collection        = self._session.collection(association_class)

        if self._guide.inverted_by:
            criteria     = collection.new_criteria()

            criteria.where('destination', self._origin.id)

            mapping_list = collection.find(criteria)

            self.extend([
                ProxyFactory.make(self._session, association.origin, self._guide)
                for association in mapping_list
            ])

            return

        criteria     = {'origin': self._origin.id}
        mapping_list = collection.filter(criteria)

        self.extend([
            ProxyFactory.make(self._session, association.destination, self._guide)
            for association in mapping_list
        ])

    def __iter__(self):
        self._prepare_list()

        return super(ProxyCollection, self).__iter__()

    def __len__(self):
        self._prepare_list()

        return super(ProxyCollection, self).__len__()

    def __contains__(self, item):
        self._prepare_list()

        return super(ProxyCollection, self).__contains__(item)

    def __delitem__(self, key):
        self._prepare_list()

        return super(ProxyCollection, self).__delitem__(key)

    def __getitem__(self, item):
        self._prepare_list()

        return super(ProxyCollection, self).__getitem__(item)

    def __getslice__(self, i, j):
        self._prepare_list()

        return super(ProxyCollection, self).__getslice__(i, j)

    def __setitem__(self, key, value):
        self._prepare_list()

        super(ProxyCollection, self).__setitem__(key, value)

class ProxyFactory(object):
    """ Proxy Factory

        This factory is to create a proxy object.

        :param session: the managed session
        :type  session: tori.db.session.Session
        :param id: the object ID
        :param mapping_guide: the relational guide
        :type  mapping_guide: tori.db.mapper.RelatingGuide
    """
    @staticmethod
    def make(session, id, mapping_guide):
        is_reverse_proxy = mapping_guide.inverted_by != None

        return ProxyObject(
            session,
            mapping_guide.target_class,
            id,
            mapping_guide.read_only or is_reverse_proxy,
            mapping_guide.cascading_options,
            is_reverse_proxy
        )