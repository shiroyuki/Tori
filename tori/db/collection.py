"""
Collection
==========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Status: Stable

The module provides a simple wrapper to work with MongoDB and Tori ORM.
"""
from tori.db.exception import MissingObjectIdException

class Collection(object):
    """
    Collection (Entity AbstractRepository) for Mongo DB

    :param em: the entity manager
    :type  em: tori.db.session.Session
    :param api: collection API
    :type  api: pymongo.collection.Collection
    :param document_class: the document class
    :type  document_class: type

    """
    def __init__(self, session, api, document_class):
        self._class   = document_class
        self._session = session
        self._api     = api
        self._has_cascading = None

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
        document = self._class(**attributes)

        return document

    def get(self, id):
        data = self._api.find_one({'_id': id})

        if not data:
            return None

        document = self._dehydrate_object(**data)

        return document

    def filter(self, criteria={}, offset=0, length=None):
        data_list = self._api.find(criteria)

        if length and isinstance(length, int):
            data_list = data_list[offset:(offset + length)]

        document_list = []

        for data in data_list:
            document = self._dehydrate_object(**data)

            document_list.append(document)

        return document_list

    def filter_one(self, criteria={}):
        raw_data = self._api.find_one(criteria)

        if not raw_data:
            return None

        document = self._dehydrate_object(**raw_data)

        return document

    def post(self, document):
        self._session._uow.register_new(document)

        document.__session__ = self._session

        return document.id

    def put(self, document):
        self._session._uow.register_update(document)

    def delete(self, document):
        self._session._uow.register_new(document)

    def commit(self):
        self._session.commit()

    def _dehydrate_object(self, **raw_data):
        if '_id' not in raw_data:
            raise MissingObjectIdException('The key _id in the raw data is not found.')

        id     = raw_data['_id']
        record = self._session._uow.find_recorded_entity(id)

        # Returned the known document from the record.
        if record:
            return record.entity

        data = dict(raw_data)

        del data['_id']

        document    = self.new(**data)
        document.id = id
        document.__session__ = self._session

        self._session.apply_relational_map(document)

        self._session._uow.register_clean(document)

        return document

    def has_cascading(self):
        if self._has_cascading is not None:
            return self._has_cascading

        self._has_cascading = False

        for property_name in self._class.__relational_map__:
            cascading_options = self._class.__relational_map__[property_name].cascading_options
            if cascading_options:
                self._has_cascading = True

                break

        return self._has_cascading

    def __len__(self):
        return self._api.count()