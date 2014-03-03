from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from tori.db.expression import Expression

class TestUnit(TestCase):
    def setUp(self):
        self.expr = Expression()

    def test_statement_parser_compile(self):
        index    = 0
        data_sets = [
            (
                'book.author = :name',
                {'right': {'value': None, 'type': 'param', 'original': ':name'}, 'left': {'value': None, 'type': 'path', 'original': 'book.author'}, 'operand': '='}
            ),
            (
                'book.title in ["Le Monde", "氷菓"]',
                {'right': {'value': ['Le Monde', '氷菓'], 'type': 'data', 'original': '["Le Monde", "氷菓"]'}, 'left': {'value': None, 'type': 'path', 'original': 'book.title'}, 'operand': 'in'}
            )
        ]

        for raw, processed in data_sets:
            compiled = self.expr._compile(raw)

            print('{}:\n  -> {}\n  <- {}'.format(index, raw, compiled))
            
            self.assertEqual(processed, compiled, 'Data set #{} failed the test.'.format(index))

            index += 1
