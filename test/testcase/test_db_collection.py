import unittest

from tori.db.document  import document, BaseDocument as BaseDocument
from tori.db.database   import Database
from tori.db.collection import Collection

@document
class Document(BaseDocument): pass

class TestDbCollection(unittest.TestCase):
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
        self.collection = Collection(
            self.db,
            Document,
            'test_orm_collection'
        )

        self.collection.delete_by_criteria()

        for data in self.test_data_set:
            d = Document(**data)
            self.collection.post(d)

    def tearDown(self):
        del self.collection

    def test_get_document(self):
        self.assertEquals(None, self.collection.get(50))

    def test_insert_document_with_predefined_id(self):
        d = Document(**self.test_new_data)

        self.assertEquals(d, self.collection.post(d))
        self.assertEquals('extra', d.id)
        self.assertEquals(5, len(self.collection))

    def test_insert_document_with_builtin_guid_generator_but_no_predefined_id(self):
        self.collection.set_guid_generator(None)

        data = dict(self.test_new_data)

        del data['_id']

        doc = Document(**data)

        self.assertEquals(doc, self.collection.post(doc))
        self.assertNotEquals('extra', doc.id)
        self.assertEquals(5, len(self.collection))

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