from unittest import TestCase, skip, skipIf

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from tori.db.manager import ManagerFactory
from tori.db.exception import InvalidUrlError
from tori.db.driver.mongodriver import Driver

class TestFunctional(TestCase):
    def setUp(self):
        self.mf = ManagerFactory()

    def test_connect(self):
        url = 'mongodb://localhost/t3test'
        manager = self.mf.connect(url)

        self.assertIsInstance(manager.driver, Driver)
