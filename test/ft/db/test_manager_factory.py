from unittest import TestCase, skip, skipIf

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from passerine.db.manager import ManagerFactory
from passerine.db.session import Session
from passerine.db.exception import InvalidUrlError
from passerine.db.driver.mongodriver import Driver

class TestFunctional(TestCase):
    def setUp(self):
        self.mf = ManagerFactory()

    def test_connect(self):
        url = 'mongodb://localhost/t3test'
        em = self.mf.connect(url)

        self.assertIsInstance(em.driver, Driver)

        session = em.open_session()

        self.assertIsInstance(session, Session)
        self.assertEqual(session.driver, em.driver)
        self.assertIsInstance(session.driver, Driver)
