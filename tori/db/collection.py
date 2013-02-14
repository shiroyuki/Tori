"""
Collection
==========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Status: Stable

The module provides a simple wrapper to work with MongoDB and Tori ORM.
"""
from tori.db.common import ProxyObject, EntityCollection
from tori.db.exception import MissingObjectIdException
from tori.db.mapper import AssociationType

class Collection(object):
    """
    Collection (Entity Repository) for Mongo DB

    :param em: the entity manager
    :type  em: tori.db.manager.Manager
    :param api: collection API
    :type  api: pymongo.collection.Collection
    :param document_class: the document class
    :type document_class: type

    """
    def __init__(self, em, api, document_class):
        self._class = document_class
        self._em    = em
        self._api   = api

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

        for property_name in self._class.__relational_map__:
            guide = self._class.__relational_map__[property_name]

            if guide.association_type in [AssociationType.ONE_TO_ONE, AssociationType.MANY_TO_ONE]:
                proxy = ProxyObject(
                    self._em,
                    guide.target_class,
                    document.__getattribute__(property_name),
                    guide.read_only,
                    guide.cascading_options
                )

                document.__setattr__(property_name, proxy)

                continue
            elif guide.association_type == AssociationType.ONE_TO_MANY:
                proxy_list = EntityCollection()

                for sub_document_attributes in document.__getattribute__(property_name):
                    proxy_list.append(
                        ProxyObject(
                            self._em,
                            guide.target_class,
                            sub_document_attributes,
                            guide.read_only,
                            guide.cascading_options
                        )
                    )

                document.__setattr__(property_name, proxy_list)

                continue

            # guide.association_type == AssociationType.MANY_TO_MANY

        return document

    def get(self, id):
        data = self._api.find_one({'_id': id})

        return self._dehydrate_object(**data)\
            if   data\
            else None

    def filter(self, criteria={}):
        data_list   = self._api.find(criteria)
        object_list = [self._dehydrate_object(**data) for data in data_list]

        return EntityCollection(object_list)

    def filter_one(self, criteria={}):
        raw_data = self._api.find_one(criteria)

        return self._dehydrate_object(**raw_data)\
            if   raw_data\
            else None

    def post(self, document):
        self._em._uow.register_new(document)

        return document.id

    def put(self, document):
        self._em._uow.register_update(document)

    def delete(self, document):
        self._em._uow.register_new(document)

    def commit(self):
        self._em.commit()

    def _dehydrate_object(self, **raw_data):
        if '_id' not in raw_data:
            raise MissingObjectIdException('The key _id in the raw data is not found.')

        id     = raw_data['_id']
        record = self._em._uow.find_recorded_entity(id)

        # Returned the known document from the record.
        if record:
            return record.entity

        data = dict(raw_data)

        del data['_id']

        document    = self.new(**data)
        document.id = id

        self._em._uow.register_clean(document)

        return document

    def __len__(self):
        return self._api.count()