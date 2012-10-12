from time import time

from imagination.decorator.validator import restrict_type
from pymongo.connection              import Connection

from tori.common import Enigma

class Collection(object):
    @restrict_type(Connection, str)
    def __init__(self, connection, database_name, document_class):
        self.db = connection.__getattr__(database_name)

        if not self.collection:
            raise Exception

    @property
    def manual(self):
        return self.db

    def get(self, document_class, id):
        collection = self.db.__getattr__(document.__name__)

        return collection.find_one({'_id': id})

    def post(self, document):
        collection = self.db.__getattr__(document.collection_name)

        return collection.insert(document)