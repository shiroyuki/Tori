# -*- coding: utf-8 -*-
"""
Repository
==========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Status: Stable
"""
import inspect
from tori.db.exception import MissingObjectIdException, NonPostableEntity, NonPutableEntity
from tori.db.mapper import AssociationType, CascadingType
from tori.db.uow import Record

class Repository(object):
    """
    Repository (Entity AbstractRepository) for Mongo DB

    :param em: the entity manager
    :type  em: tori.db.session.Session
    :param api: collection API
    :type  api: pymongo.collection.Collection
    :param representing_class: the representing class
    :type  representing_class: type

    """
    def __init__(self, session, representing_class):
        self._class   = representing_class
        self._session = session

        self._has_cascading = None

        # Retrieve the collection
        self._api = session.db[representing_class.__collection_name__]
        self._session.register_class(representing_class)

    @property
    def name(self):
        return self._class.__collection_name__

    def new(self, **attributes):
        """ Create a new document/entity

        :param attributes: attribute map
        :return: object

        .. note::

            This method deal with data mapping

        """
        spec = inspect.getargspec(self._class.__init__) # constructor contract
        rmap = self._class.__relational_map__ # relational map

        # Default missing argument to NULL or LIST
        # todo: respect the default value of the argument
        for argument_name in spec.args:
            if argument_name == 'self' or argument_name in attributes:
                continue

            default_to_list = argument_name in rmap\
                and rmap[argument_name].association in [
                    AssociationType.ONE_TO_MANY,
                    AssociationType.MANY_TO_MANY
                ]

            attributes[argument_name] = [] if default_to_list else None

        attribute_name_list = list(attributes.keys())

        # Remove unwanted arguments/attributes/properties
        for attribute_name in attribute_name_list:
            if argument_name == 'self' or attribute_name in spec.args:
                continue

            del attributes[attribute_name]

        return self._class(**attributes)

    def get(self, id):
        data = self._api.find_one({'_id': id})

        if not data:
            return None

        return self._dehydrate_object(data)

    def filter(self, criteria={}, offset=0, length=None):
        data_list = self._api.find(criteria)

        if length and isinstance(length, int):
            data_list = data_list[offset:(offset + length)]

        entity_list = []

        for data in data_list:
            entity = self._dehydrate_object(data)
            record = self._session.find_record(id, self._class)

            if record and record.status in [Record.STATUS_DELETED, Record.STATUS_IGNORED]:
                continue

            entity_list.append(entity)

        return entity_list

    def filter_one(self, criteria={}):
        raw_data = self._api.find_one(criteria)

        if not raw_data:
            return None

        return self._dehydrate_object(raw_data)

    def post(self, entity):
        if entity.id or entity.__session__:
            raise NonPostableEntity('')

        self._session.persist(entity)

        entity.__session__ = self._session

        self.commit()

        return entity.id

    def put(self, entity):
        if not entity.id or not entity.__session__:
            raise NonPutableEntity('')

        self._session.persist(entity)
        self.commit()

    def delete(self, entity):
        self._session.delete(entity)
        self.commit()

    def persist(self, entity):
        self._session.persist(entity)

    def commit(self):
        self._session.flush()

    def _dehydrate_object(self, raw_data):
        if '_id' not in raw_data:
            raise MissingObjectIdException('The key _id in the raw data is not found.')

        id     = raw_data['_id']
        record = self._session.find_record(id, self._class)

        # Returned the known document from the record.
        if record:
            return record.entity

        data = dict(raw_data)

        del data['_id']

        document    = self.new(**data)
        document.id = id
        document.__session__ = self._session

        self._session.apply_relational_map(document)
        self._session.recognize(document)

        return document

    def has_cascading(self):
        if self._has_cascading is not None:
            return self._has_cascading

        self._has_cascading = False

        for property_name in self._class.__relational_map__:
            cascading_options = self._class.__relational_map__[property_name].cascading_options

            if cascading_options and CascadingType.DELETE in cascading_options:
                self._has_cascading = True

                break

        return self._has_cascading

    def __len__(self):
        return self._api.count()