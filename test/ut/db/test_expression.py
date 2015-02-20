# -*- coding: utf-8 -*-

from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from passerine.db.expression import Criteria, ExpressionPart, InvalidExpressionError

class TestUnit(TestCase):
    def setUp(self):
        self.expr = Criteria()

    def test_statement_parser_compile_ok(self):
        index     = 0
        data_sets = [
            (
                'book.author = :name',
                '='
            ),
            (
                'book.title in ["Le Monde", "氷菓"]',
                'in'
            ),
            (
                'book indexed with ["light-novel", "japanese", "mystery"]',
                'indexed with'
            )
        ]

        for raw, expected_operand in data_sets:
            compiled = self.expr._compile(raw)

            self.assertEqual(expected_operand, compiled.operand, 'Data set #{} failed the test.'.format(index))

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
                print('{}: {}'.format(index, raw))

                index += 1

                compiled = self.expr._compile(raw)
