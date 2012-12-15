import unittest

from tori.db.exception import LockedIdException, ReservedAttributeException
from tori.db.document  import BaseDocument
from tori.db.document  import document

@document('PowerfulPeople')
class Boss(BaseDocument): pass

@document
class Person(BaseDocument): pass

@document
class Organization(object):
    def __init__(self, name):
        self.name = name.capitalize()

class TestDbDocument(unittest.TestCase):
    test_attributes = {
        'name': 'Juti',
        'occupation': 'Developer'
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        pass
