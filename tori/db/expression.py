# -*- coding: utf-8 -*-

import json
import re

class SyntaxError(Exception):
    """ Expression Syntax Error """

class Expression(object):
    """ Query Expression

        Support operands: =, <=, <, >, >=, in, like (SQL-like string pattern), rlike (Regular-expression pattern), indexed with (only for Riak)
    """

    OP_EQ = '='
    OP_GE = '>='
    OP_GT = '>'
    OP_LE = '<='
    OP_LT = '<'
    OP_IN = 'in'
    OP_SQL_LIKE     = 'like'
    OP_REGEXP_LIKE  = 'rlike'
    OP_INDEX_SEARCH = 'indexed_with'

    IS_PARAMETER     = 'param'
    IS_PROPERTY_PATH = 'path'
    IS_DATA          = 'data'

    def __init__(self, alias):
        self._sub_expressions = []
        self._re_statement = re.compile(
            '^\s*(?P<left>.+)\s+(?P<operand>{eq}|{ge}|{gt}|{le}|{lt}|{xin}|{like}|{rlike}|{indexed})\s+(?P<right>.+)\s*$'.format(
                eq = Expression.OP_EQ,
                ge = Expression.OP_GE,
                gt = Expression.OP_GT,
                le = Expression.OP_LE,
                lt = Expression.OP_LT,
                xin  = Expression.OP_IN,
                like = Expression.OP_SQL_LIKE,
                rlike   = Expression.OP_REGEXP_LIKE,
                indexed = Expression.OP_INDEX_SEARCH
            )
        )
        self._re_parameter = re.compile('^:[a-zA-Z0-9_]+$')
        self._re_property_path = re.compile('^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)+$')
        self._re_list = re.compile('^\[.+\]$')
        self._re_dict = re.compile('^\{.+\}$')
        self._re_integer = re.compile('^\d+$')
        self._re_float = re.compile('^\d*\.\d+$')
        self._re_boolean_true = re.compile('^(T|t)rue$')
        self._re_boolean_false = re.compile('^(F|f)alse$')

    @property
    def sub_expressions(self):
        return self._sub_expressions

    def expect(self, statement):
        expr = self._compile(statement);

        self._sub_expressions.append(expr)

    def _compile(self, statement):
        fixed_syntax_operands = ('in', 'like', 'rlike', 'indexed with')

        expr = self._parse(statement)

        expr['left']  = self._parse_side(expr['left'])
        expr['right'] = self._parse_side(expr['right'])

        # Validate the syntax
        if expr['left']['type'] != Expression.IS_PROPERTY_PATH and expr['operand'] in fixed_syntax_operands:
            raise SyntaxError('The property path must be on the left of the operand.')

        if expr['right']['type'] == Expression.IS_PROPERTY_PATH and expr['operand'] in fixed_syntax_operands:
            raise SyntaxError('The property path cannot be on the right of the operand.')

        # to be continued

        return expr

    def _parse_side(self, sub_statement):
        kind = Expression.IS_DATA

        if self._re_parameter.match(sub_statement):
            kind = Expression.IS_PARAMETER

        elif self._re_property_path.match(sub_statement):
            kind = Expression.IS_PROPERTY_PATH

        if kind != Expression.IS_DATA:
            return {
                'original': sub_statement,
                'type':     kind,
                'value':    None
            }

        return {
            'original': sub_statement,
            'type':     kind,
            'value':    json.loads(sub_statement)
        }

    def _parse(self, statement):
        matches = self._re_statement.match(statement)

        if not matches:
            raise SyntaxError('Incomplete statement: {}'.format(statement))

        expr = matches.groupdict()

        return expr