'''
:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Availability: DEV
:Stability: Experimental
'''

from time import time

class Collection(object):
    '''
    :type database: :class:`tori.db.odm.database.Database`
    '''
    def __init__(self, database, name, document_class):
        self._collection = None
        self._name       = name
        self._database   = database
        self._class      = document_class

    @property
    def api(self):
        if not self._collection:
            self._collection = self._database.collection(self._name)

        return self._collection

    def new_document(self, **attributes):
        return self._class(**attributes)

    def _convert_to_object(self, **raw_data):
        document = self.new_document(**raw_data)
        document.reset_bits()

        return document

    def get(self, id):
        raw_data = self.api.find_one({'_id': id})

        return self._convert_to_object(**raw_data)

    def filter(self, **criteria):
        raw_data_list = self.api.find(criteria)

        return [self._convert_to_object(**raw_data) for raw_data in raw_data_list]\
            if   raw_data_list.count()\
            else []

    def filter_one(self, **criteria):
        raw_data_list = self.api.find_one(criteria)

        return [self._convert_to_object(**raw_data) for raw_data in raw_data_list]\
            if   raw_data_list.count()\
            else []

    def post(self, document):
        cs = document.get_changeset()
        id = self.api.insert(cs, safe=True)

        if not document.id:
            document.id = id

        document.reset_bits()

        return document

    def put(self, document, upsert=False):
        self.api.update(document.get_changeset(), upsert=upsert)

        document.reset_bits()

        return document

    def delete(self, id):
        self.api.remove({'_id': id})

    def delete_by_criteria(self, **criteria):
        criteria = criteria or {}

        self.api.remove(criteria)

    def __len__(self):
        return self.api.count()