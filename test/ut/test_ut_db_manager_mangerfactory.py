from unittest import TestCase, skip, skipIf

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from tori.db.manager import ManagerFactory
from tori.db.exception import InvalidUrlError

class TestUnit(TestCase):
    def setUp(self):
        self.mf = ManagerFactory()

    def test_analyze_url_ok(self):
        url = 'dbp://user:password@tori.shiroyuki.com/database_name'

        expected_result = {
            'protocol': 'dbp',
            'address':  'user:password@tori.shiroyuki.com/database_name'
        }

        actual_result = self.mf.analyze_url(url)

        self.assertEqual(expected_result, actual_result)
    
    def test_analyze_url_error(self):
        urls = [
            '://user:password@tori.shiroyuki.com/database_name',
            '-://user:password@tori.shiroyuki.com/database_name',
            'mongodb://',
            'mongodb:/abc'
        ]

        for url in urls:
            with self.assertRaises(InvalidUrlError):
                actual_result = self.mf.analyze_url(url)
