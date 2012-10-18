import unittest

from pymongo.connection import Connection

from tori.db.odm.exception  import *
from tori.db.odm.database   import Database
from tori.db.odm.collection import Collection
from tori.db.odm.document   import document, Document as BaseDocument

@document
class Document(BaseDocument): pass

class TestDbOdmCollection(unittest.TestCase):
    test_data_set = [
        {
            '_id':   1,
            'title': 'Python'
        },
        {
            '_id':   2,
            'title': 'PHP',
        },
        {
            '_id':   3,
            'title': 'Ruby'
        },
        {
            'title': 'Scala'
        }
    ]

    db = Database('tori_test')
    collection = None

    def setUp(self):
        self.collection = self.collection or Collection(
            self.db,
            'test_orm_collection',
            Document
        )

        self.collection.delete_by_criteria()
        self.assertEquals(0, len(self.collection))

    def tearDown(self):
        pass

    def test_get_document(self):
        self.assertEquals(None, self.collection.get(1))

    def test_insert_document_with_predefined_id(self):
        d = Document(**self.test_data_set[0])

        self.assertEquals(d, self.collection.post(d))
        self.assertEquals(1, len(self.collection))

    def test_insert_document_without_predefined_id(self):
        d = Document(**self.test_data_set[3])

        self.assertEquals(None, d.id)
        self.assertEquals(d, self.collection.post(d))
        self.assertNotEquals(None, d.id)
        self.assertEquals(1, len(self.collection))

    def test_delete_document_by_id(self):
        for data in self.test_data_set:
            d = Document(**data)

            self.collection.post(d)

        # First delete
        self.collection.delete(2)
        self.assertEquals(3, len(self.collection))

        # Make sure that the second delete won't throw errors or delete others.
        self.collection.delete(2)
        self.assertEquals(3, len(self.collection))
