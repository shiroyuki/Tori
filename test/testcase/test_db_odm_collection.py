import unittest

from pymongo.connection import Connection

from tori.db.odm.exception  import *
from tori.db.odm.database   import Database
from tori.db.odm.collection import Collection
from tori.db.odm.document   import document, Document as BaseDocument

@document
class Document(BaseDocument): pass

class TestDbOdmCollection(unittest.TestCase):
    test_attributes = {
        'name': 'Juti',
        'occupation': 'Developer'
    }

    db = Database('tori_test')
    collection = None

    def setUp(self):
        self.collection = self.collection or Collection(
            self.db,
            'test_orm_collection',
            Document
        )

        self.collection.delete_by_criteria()

    def tearDown(self):
        pass

    def test_insert_document(self):
        d = Document(**self.test_attributes)
        d.id = 1

        self.assertEquals(d, self.collection.post(d))
        self.assertEquals(1, len(self.collection))
