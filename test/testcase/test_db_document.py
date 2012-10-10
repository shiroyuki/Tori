import unittest

from tori.exception   import ODMDocumentIdLocked
from tori.db.document import Document

class Person(Document): pass

class TestDocument(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_new_document(self):
        person = Person(name='Juti', occupation='Software Developer')

        self.assertEquals('person', person.collection_name)

        self.assertEquals(None, person.id)
        self.assertEquals('Juti', person.name)
        self.assertFalse(person.is_dirty('name'))

    def test_old_document(self):
        person = Person(_id=1, name='Juti', occupation='Software Developer')

        self.assertEquals(1, person.id)

        with self.assertRaises(ODMDocumentIdLocked):
            person._id = 2

    def test_old_document_on_updating_existing_attribute(self):
        person = Person(_id=1, name='Juti', occupation='Software Developer')

        self.assertEquals(1, person.id)
        self.assertFalse(person.is_dirty('name'))

        person.name = 'Obiwan'

        self.assertEquals('Obiwan', person.name)
        self.assertTrue(person.is_dirty('name'))

    def test_old_document(self):
        person = Person(_id=1, name='Juti', occupation='Software Developer')

        self.assertEquals(1, person.id)

        with self.assertRaises(AttributeError):
            person.is_dirty('is_awesome')

        person.is_awesome = True

        self.assertTrue(person.is_awesome)
        self.assertTrue(person.is_dirty('is_awesome'))