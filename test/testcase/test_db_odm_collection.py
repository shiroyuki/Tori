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
            'title': 'Python',
            'rank':  1
        },
        {
            '_id':   2,
            'title': 'PHP',
            'rank':  1
        },
        {
            '_id':   3,
            'title': 'Ruby',
            'rank':  2
        },
        {
            'title': 'C',
            'rank':  1
        }
    ]

    test_new_data = {
        '_id':   'extra',
        'title': 'Java',
        'rank':  3
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

        for data in self.test_data_set:
            d = Document(**data)
            self.collection.post(d)

    def tearDown(self):
        pass

    def test_get_document(self):
        self.assertEquals(None, self.collection.get(50))

    def test_insert_document_with_predefined_id(self):
        d = Document(**self.test_new_data)

        self.assertEquals(d, self.collection.post(d))
        self.assertEquals('extra', d.id)
        self.assertEquals(5, len(self.collection))

    def test_insert_document_without_predefined_id(self):
        # Part of the data fixtures
        d = self.collection.filter_one(title='C')

        self.assertNotEquals(None, d.id)
        self.assertTrue(type(d.id) != int)
        self.assertEquals(4, len(self.collection))

    def test_delete_document_by_id(self):
        # First delete
        self.collection.delete(2)
        self.assertEquals(3, len(self.collection))

        # Make sure that the second delete won't throw errors or delete others.
        self.collection.delete(2)
        self.assertEquals(3, len(self.collection))

    def test_update_document(self):
        updated_title = u'C++'

        d = self.collection.filter_one(title='C')
        d_id = d.id

        d.title = updated_title

        changeset = d.get_changeset()

        self.assertTrue('title' in changeset)
        self.assertFalse('rank' in changeset)

        self.collection.put(d)

        d_updated = self.collection.get(d_id)

        self.assertEquals(d_id, d.id)
        self.assertEquals(d.id, d_updated.id)
        self.assertEquals(d.rank, d_updated.rank)
        self.assertEquals(d.title, d_updated.title)
        self.assertEquals(4, len(self.collection))