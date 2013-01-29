"""
Collection
==========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Status: Stable

The module provides a simple wrapper to work with MongoDB and Tori ORM.
"""

class Collection(object):
    """
    Collection (Entity Repository) for Mongo DB

    :param em: the entity manager
    :type em: tori.db.manager.Manager
    :param document_class: the document class
    :type document_class: type

    """
    def __init__(self, em, document_class):
        self._class = document_class
        self._em    = em

        self._name = self._class.__collection_name__
        self._api  = self._em.collection(self._name)

    @property
    def name(self):
        return self._name

    def new(self, **attributes):
        return self._class(**attributes)

    def get(self, id):
        raw_data = self._api.find_one({'_id': id})

        return self._convert_to_object(**raw_data)\
            if   raw_data\
            else None

    def filter(self, **criteria):
        raw_data_list = self._api.find(criteria)

        return [self._convert_to_object(**raw_data) for raw_data in raw_data_list]\
            if   raw_data_list.count()\
            else []

    def filter_one(self, **criteria):
        raw_data = self._api.find_one(criteria)

        return self._convert_to_object(**raw_data)\
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

    def __len__(self):
        return self._api.count()