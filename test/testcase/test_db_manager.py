import unittest

from tori.db.document  import document, BaseDocument as BaseDocument
from tori.db.database   import Database
from tori.db.collection import Collection

@document
class Document(BaseDocument): pass

class TestDbManager(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        pass
