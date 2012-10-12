import unittest

from pymongo import Connection

from tori.db.odm.exception  import LockedIdException, ReservedAttributeException
from tori.db.odm.collection import Collection
from tori.db.odm.document   import document, Document

@document
class Person(Document): pass

class TestDbOdmDocument(unittest.TestCase):
    test_attributes = {
        'name': 'Juti',
        'occupation': 'Developer'
    }

    collection = None

    #def setUp(self):
    #    self.collection = Collection(
    #        Connection('localhost'),
    #        'test_sandbox'
    #    )
    #
    #def tearDown(self):
    #    pass
    #
    #def test_new_document(self):
    #    person = Person(**self.test_attributes)
    #
    #    c = self.collection.manual
    #
    #    print dir(c)
    #
    #    #self.collection.manual.insert(person)
