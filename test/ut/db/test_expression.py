# -*- coding: utf-8 -*-

from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from tori.db.expression import Expression, InvalidExpressionError

class TestUnit(TestCase):
    def setUp(self):
        self.expr = Expression('u')

    def test_statement_parser_compile_ok(self):
        index     = 0
        data_sets = [
            (
                'book.author = :name',
                {'right': {'value': None, 'type': 'param', 'original': ':name'}, 'left': {'value': None, 'type': 'path', 'original': 'book.author'}, 'operand': '='}
            ),
            (
                'book.title in ["Le Monde", "氷菓"]',
                {'right': {'value': [u'Le Monde', u'氷菓'], 'type': 'data', 'original': '["Le Monde", "氷菓"]'}, 'left': {'value': None, 'type': 'path', 'original': 'book.title'}, 'operand': 'in'}
            )
        ]

        for raw, processed in data_sets:
            compiled = self.expr._compile(raw)

            print('{}:\n  RAW -> {}\n  CPE <- {}\n  EXE <- {}'.format(index, raw, compiled, processed))

            self.assertEqual(processed, compiled, 'Data set #{} failed the test.'.format(index))

            index += 1

    def test_statement_parser_compile_raises_invalid_expression_error(self):
        index     = 0
        data_sets = [
            'book.author = "__',
            '35126 in [3, 5, 2]',
            ':goo in :mama',
            'a =',
            'a = 1'
        ]

        for raw in data_sets:
            with self.assertRaises(InvalidExpressionError):
                compiled = self.expr._compile(raw)
