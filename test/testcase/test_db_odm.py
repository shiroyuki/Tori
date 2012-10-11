import unittest

from tori.db.odm.exception import LockedIdException, ReservedAttributeException
from tori.db.odm.document  import Document

class Person(Document): pass

class TestDocument(unittest.TestCase):
    test_attributes = {
        'name': 'Juti',
        'occupation': 'Developer'
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_new_document(self):
        person = Person(**self.test_attributes)

        self.assertEquals('person', person.collection_name)

        self.assertEquals(None, person.id)
        self.assertEquals('Juti', person.name)
        self.assertFalse(person.is_dirty('name'))
        self.assertEquals('test_db_odm.Person', person.get_class_name())

    def test_new_document_changeset(self):
        person = Person(**self.test_attributes)

        changeset = person.get_changeset()

        for name in self.test_attributes:
            self.assertTrue(name in changeset)
            self.assertEquals(self.test_attributes[name], changeset[name])

        self.assertTrue(changeset)

    def test_old_document(self):
        person = Person(_id=1, **self.test_attributes)

        self.assertEquals(1, person.id)
        self.assertFalse(person.get_changeset())

    def test_old_document_on_adding_new_attribute(self):
        person = Person(_id=1, **self.test_attributes)

        self.assertEquals(1, person.id)

        with self.assertRaises(AttributeError):
            self.assertFalse(person.is_dirty('is_awesome'))

        with self.assertRaises(AttributeError):
            person.is_dirty('is_awesome')

        person.is_awesome = True

        self.assertTrue(person.is_awesome)
        self.assertTrue(person.is_dirty('is_awesome'))

    def test_old_document_on_updating_existing_attribute(self):
        person = Person(_id=1, **self.test_attributes)

        self.assertFalse(person.is_dirty('name'))

        person.name = 'Obiwan'

        self.assertEquals('Obiwan', person.name)
        self.assertTrue(person.is_dirty('name'))

    def test_old_document_on_updating_existing_attribute_with_correct_changeset(self):
        person = Person(_id=1, **self.test_attributes)

        person.name = 'Obiwan'

        changeset = person.get_changeset()

        self.assertTrue('_id' in changeset)
        self.assertTrue('name' in changeset)
        self.assertFalse('occupation' in changeset)

    def test_old_document_failed_on_attempt_to_change_id(self):
        person = Person(_id=1, **self.test_attributes)

        with self.assertRaises(LockedIdException):
            person.id = 2

        with self.assertRaises(ReservedAttributeException):
            person._id = 2

    def test_document_failed_to_update_reserved_attributes(self):
        person = Person(_id=1, **self.test_attributes)

        with self.assertRaises(ReservedAttributeException):
            person.is_dirty = 2

        with self.assertRaises(ReservedAttributeException):
            person.collection_name = 'asdf'

    def test_document_failed_to_check_unknown_attribute(self):
        person = Person(_id=1, **self.test_attributes)

        with self.assertRaises(AttributeError):
            self.assertFalse(person.is_dirty('is_dirty'))