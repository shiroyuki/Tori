import unittest
from bson import ObjectId
from tori.db.common import Serializer, PseudoObjectId
from tori.db.entity import entity

@entity
class Document(object):
    def __init__(self, name):
        self.name = name

class TestFunctional(unittest.TestCase):
    def setUp(self):
        self.s = Serializer()

    def tearDown(self):
        pass

    def test_document_without_id(self):
        doc = Document('shiroyuki')

        encoded_doc = self.s.encode(doc)

        self.assertFalse('_id' in encoded_doc)
        self.assertFalse('id' in encoded_doc)
        self.assertEqual(encoded_doc['name'], 'shiroyuki')

    def test_document_with_pseudo_id(self):
        doc = Document('shiroyuki')

        doc.id = PseudoObjectId()

        encoded_doc = self.s.encode(doc)

        self.assertFalse('_id' in encoded_doc)
        self.assertFalse('id' in encoded_doc)
        self.assertEqual(encoded_doc['name'], 'shiroyuki')

    def test_document_with_actual_id(self):
        doc = Document('shiroyuki')

        doc.id = ObjectId()

        encoded_doc = self.s.encode(doc)

        self.assertTrue('_id' in encoded_doc)
        self.assertFalse('id' in encoded_doc)
        self.assertEqual(encoded_doc['name'], 'shiroyuki')