from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from bson import ObjectId
from tori.db.common import PseudoObjectId
from tori.db.entity import entity
from tori.db.exception import MissingObjectIdException, EntityAlreadyRecognized, EntityNotRecognized
from tori.db.repository import Repository
from tori.db.session import Session

@entity('test_tori_db_repository_data')
class Data(object): pass

class TestUnit(TestCase):
    def setUp(self):
        pass

    @patch('tori.db.session.Session')
    def test_positive_post(self, session):
        repository = Repository(session, Data)

        data = Data()
        data.__session__ = None

        repository.post(data)

        session.persist.assert_called_with(data)
        session.flush.assert_called_with()

    @patch('tori.db.session.Session')
    def test_negative_post(self, session):
        repository = Repository(session, Data)

        data = Data()
        data.__session__ = True

        with self.assertRaises(EntityAlreadyRecognized):
            repository.post(data)

    @patch('tori.db.session.Session')
    def test_positive_put(self, session):
        repository = Repository(session, Data)

        a = Data()
        a.id = ObjectId()
        a.__session__ = True

        repository.put(a)

        session.persist.assert_called_with(a)
        session.flush.assert_called_with()

    @patch('tori.db.session.Session')
    def test_negative_put_without_session(self, session):
        repository = Repository(session, Data)

        a = Data()
        a.id = ObjectId()

        with self.assertRaises(EntityNotRecognized):
            repository.put(a)

    @patch('tori.db.session.Session')
    def test_negative_put_without_id(self, session):
        repository = Repository(session, Data)

        a = Data()
        a.__session__ = True

        with self.assertRaises(EntityNotRecognized):
            repository.put(a)

    @patch('tori.db.session.Session')
    def test_negative_put_with_pseudo_id(self, session):
        repository = Repository(session, Data)

        a = Data()
        a.id = PseudoObjectId()
        a.__session__ = True

        with self.assertRaises(EntityNotRecognized):
            repository.put(a)

    @patch('tori.db.session.Session')
    def test_positive_delete(self, session):
        repository = Repository(session, Data)

        a = Data()
        a.id = 1
        a.__session__ = True

        repository.delete(a)

        session.delete.assert_called_with(a)
        session.flush.assert_called_with()

    @patch('tori.db.session.Session')
    def test_negative_delete_random(self, session):
        repository = Repository(session, Data)

        a = Data()
        a.id = PseudoObjectId()
        a.__session__ = True

        with self.assertRaises(EntityNotRecognized):
            repository.put(a)