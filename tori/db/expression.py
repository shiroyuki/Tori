# -*- coding: utf-8 -*-

import json
import re

class InvalidExpressionError(Exception):
    """ Generic Invalid Expression Error """

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
    OP_INDEX_SEARCH = 'indexed with'

    IS_PARAMETER     = 'param'
    IS_PROPERTY_PATH = 'path'
    IS_DATA          = 'data'

    def __init__(self):
        self._is_updated       = False
        self._sub_expressions  = []
        self._analyzed_map     = None
        self._re_parameter     = re.compile('^:[a-zA-Z0-9_]+$')
        self._re_root_path     = re.compile('^[a-zA-Z][a-zA-Z0-9_]*$')
        self._re_property_path = re.compile('^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$')
        self._re_statement     = re.compile(
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

    def get_analyzed_version(self):
        if self._is_updated:
            return self._analyzed_map

        reference_map = {
            # Property-path-to-class map
            'properties': {},
            # Parameter-to-value map
            'parameters': {},
            'expressions': self._sub_expressions
        }

        # Scan for all property paths and parameters.
        for se in self._sub_expressions:
            self._scan_for_property_paths_and_parameters(reference_map, se['left'])
            self._scan_for_property_paths_and_parameters(reference_map, se['right'])

        if not reference_map['properties']:
            raise InvalidExpressionError('There must be at least one property path. It is prone to query injection.')

        self._analyzed_map = reference_map

        return self._analyzed_map

    def _scan_for_property_paths_and_parameters(self, reference_map, sub_expression_part):
        """ Search for all property paths and parameters.
        """
        # Search for all referred property paths.
        if sub_expression_part['type'] == Expression.IS_PROPERTY_PATH:
            property_path = sub_expression_part['original']

            reference_map['properties'][property_path] = None

        # Search for all referred property paths.
        if sub_expression_part['type'] == Expression.IS_PARAMETER:
            parameter_name = sub_expression_part['original'][1:]

            reference_map['parameters'][parameter_name] = None

    def expect(self, statement):
        self._is_updated = False

        expr = self._compile(statement)

        self._sub_expressions.append(expr)

    @property
    def _fixed_syntax_operands(self):
        return ('in', 'like', 'rlike', 'indexed with')

    def _compile(self, statement):
        fixed_syntax_operands = self._fixed_syntax_operands

        expr = self._parse(statement)

        try:
            expr['left']  = self._parse_side(expr['left'])
        except InvalidExpressionError as exception:
            raise InvalidExpressionError('The left side of the expression cannot be parsed.')

        try:
            expr['right']  = self._parse_side(expr['right'])
        except InvalidExpressionError as exception:
            raise InvalidExpressionError('The left side of the expression cannot be parsed.')

        # Validate the syntax on the fixed syntaxes.
        if expr['operand'] in fixed_syntax_operands:
            if expr['left']['type'] != Expression.IS_PROPERTY_PATH:
                raise InvalidExpressionError('The property path must be on the left of the operand.')

            if expr['right']['type'] == Expression.IS_PROPERTY_PATH:
                raise InvalidExpressionError('The property path cannot be on the right of the operand.')

        # If the left side refers to the root path but not for the index search,
        # the method will raise the invalid expression error.
        if expr['left']['type'] == Expression.IS_PROPERTY_PATH \
            and '.' not in expr['left']['original'] \
            and expr['operand'] != Expression.OP_INDEX_SEARCH:
            raise InvalidExpressionError('The property path to the root entity can only be used by index search.')

        # The property path must be in the expression.
        if expr['left']['type'] != Expression.IS_PROPERTY_PATH and expr['right']['type'] != Expression.IS_PROPERTY_PATH:
            raise InvalidExpressionError('The property path must be in the expression.')

        return expr

    def _parse_side(self, sub_statement):
        kind = Expression.IS_DATA

        if self._re_parameter.match(sub_statement):
            kind = Expression.IS_PARAMETER

        elif self._re_property_path.match(sub_statement) or self._re_root_path.match(sub_statement):
            kind = Expression.IS_PROPERTY_PATH

        if kind != Expression.IS_DATA:
            return {
                'original': sub_statement,
                'type':     kind,
                'value':    None
            }

        decoded_data = None

        try:
            decoded_data = json.loads(sub_statement)
        except ValueError as exception:
            raise InvalidExpressionError('Unable to decode the data.')

        return {
            'original': sub_statement,
            'type':     kind,
            'value':    decoded_data
        }

    def _parse(self, statement):
        matches = self._re_statement.match(statement)

        if not matches:
            raise InvalidExpressionError('Incomplete statement: {}'.format(statement))

        expr = matches.groupdict()

        return expr