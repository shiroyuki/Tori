"""
Collection
==========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Status: Stable

The module provides a simple wrapper to work with MongoDB and Tori ORM.
"""

from tori.db.common import GuidGenerator

class Collection(object):
    """
    Collection (Entity Repository) for Mongo DB

    :param database: the database connection
    :type database: tori.db.database.Database
    :param document_class: the document class
    :type document_class: type
    :param name: the name of the collection (default: use class's collection name)
    :type name: str
    :param guid_generator: the GUID generator (default: use the generic built-in generator)
    :type guid_generator: tori.db.common.GuidGenerator

    """
    def __init__(self, database, document_class, name=None, guid_generator=None):
        self._collection = None
        self._name       = name or document_class.__collection_name__
        self._database   = database
        self._class      = document_class
        self._guid_generator = guid_generator or GuidGenerator()

    @property
    def api(self):
        if not self._collection:
            self._collection = self._database.collection(self._name)

        return self._collection

    @property
    def name(self):
        return self._name

    def set_guid_generator(self, guid_generator):
        self._guid_generator = guid_generator

    def new_document(self, **attributes):
        return self._class(**attributes)

    def _convert_to_object(self, **raw_data):
        document = self.new_document(**raw_data)
        document.reset_bits()

        return document

    def get(self, id):
        raw_data = self.api.find_one({'_id': id})

        return self._convert_to_object(**raw_data)\
            if   raw_data\
            else None

    def filter(self, **criteria):
        raw_data_list = self.api.find(criteria)

        return [self._convert_to_object(**raw_data) for raw_data in raw_data_list]\
            if   raw_data_list.count()\
            else []

    def filter_one(self, **criteria):
        raw_data = self.api.find_one(criteria)

        return self._convert_to_object(**raw_data)\
            if   raw_data\
            else None

    def post(self, document):
        if not document.id:
            document.id = self._guid_generator.generate()

        cs = document.get_changeset()
        id = self.api.insert(cs, safe=True)

        document.reset_bits()

        return document

    def put(self, document, upsert=False, replace=False):
        changeset = document.get_changeset(not replace)

        if replace:
            update_instruction = changeset
        else:
            del changeset['_id']

            update_instruction = {'$set': changeset}

        self.api.update({'_id': document.id}, update_instruction, upsert=upsert)

        document.reset_bits()

        return document

    def delete(self, id):
        self.api.remove({'_id': id})

    def delete_by_criteria(self, **criteria):
        criteria = criteria or {}

        self.api.remove(criteria)

    def __len__(self):
        return self.api.count()