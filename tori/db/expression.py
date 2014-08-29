# -*- coding: utf-8 -*-
import json
import re

class InvalidExpressionError(Exception):
    """ Generic Invalid Expression Error """

class DataObject(object):
    @property
    def in_json(self):
        raise RuntimeError('Unknown data object')

    def __str__(self):
        return str(self.in_json)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__str__())

class ExpressionOperand(object):
    OP_EQ = '='
    OP_NE = '!='
    OP_GE = '>='
    OP_GT = '>'
    OP_LE = '<='
    OP_LT = '<'
    OP_IN = 'in'
    OP_NOT_IN = 'not in'
    OP_SQL_LIKE     = 'like'
    OP_REGEXP_LIKE  = 'rlike'
    OP_INDEX_SEARCH = 'indexed with'

class ExpressionType(object):
    IS_PARAMETER     = 'param'
    IS_PROPERTY_PATH = 'path'
    IS_DATA          = 'data'

class Expression(DataObject):
    """ Query Expression

        :param tori.db.expression.ExpressionPart left:  the left part
        :param tori.db.expression.ExpressionPart right: the right part
        :param str operand: the generic operand
    """
    def __init__(self, left, operand, right):
        self.left = left
        self.operand = operand
        self.right = right

    @property
    def in_json(self):
        return {
            'left': self.left,
            'right': self.right,
            'operand': self.operand
        }

    def __str__(self):
        return '{left} {operand} {right}'.format(
            left    = self.left.original,
            right   = self.right.original,
            operand = self.operand
        )

class ExpressionPart(DataObject):
    """ Query Expression

        :param str original: the original query
        :param str kind:     the type of the part
        :param     value:    the parameter value only for a data part
        :param str alias:    the entity alias for a property part or the name of the parameter of a parameter part
    """
    def __init__(self, original, kind, value, alias):
        self.original = original
        self.kind     = kind
        self.value    = value
        self.alias    = alias

    @property
    def in_json(self):
        return {
            'original': self.original,
            'kind':     self.kind,
            'value':    self.value,
            'alias':    self.alias
        }

class ExpressionSet(DataObject):
    """ Representation of Analyzed Expression """
    def __init__(self, expressions):
        self.properties  = {}
        self.parameters  = []
        self.expressions = expressions

    @property
    def in_json(self):
        return {
            'properties':  self.properties,
            'parameters':  self.parameters,
            'expressions': self.expressions
        }

class Criteria(object):
    """ Expression Criteria

        Support operands: =, <=, <, >, >=, in, like (SQL-like string pattern), rlike (Regular-expression pattern), indexed with (only for Riak)
    """

    def __init__(self):
        self._is_updated       = False
        self._sub_expressions  = []
        self._analyzed_map     = None
        self._re_parameter     = re.compile('^:[a-zA-Z0-9_]+$')
        self._re_root_path     = re.compile('^[a-zA-Z][a-zA-Z0-9_]*$')
        self._re_property_path = re.compile('^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$')
        self._re_statement     = re.compile(
            '^\s*(?P<left>.+)\s+(?P<operand>{eq}|{ne}|{ge}|{gt}|{le}|{lt}|{xin}|{xnin}|{like}|{rlike}|{indexed})\s+(?P<right>.+)\s*$'.format(
                eq = ExpressionOperand.OP_EQ,
                ne = ExpressionOperand.OP_NE,
                ge = ExpressionOperand.OP_GE,
                gt = ExpressionOperand.OP_GT,
                le = ExpressionOperand.OP_LE,
                lt = ExpressionOperand.OP_LT,
                xin  = ExpressionOperand.OP_IN,
                xnin = ExpressionOperand.OP_NOT_IN,
                like = ExpressionOperand.OP_SQL_LIKE,
                rlike   = ExpressionOperand.OP_REGEXP_LIKE,
                indexed = ExpressionOperand.OP_INDEX_SEARCH
            )
        )
        self._re_property_path_delimiter = re.compile('\.')

    def get_analyzed_version(self):
        if self._is_updated:
            return self._analyzed_map

        analyzed_expression = ExpressionSet(self._sub_expressions)

        # Scan for all property paths and parameters.
        for se in self._sub_expressions:
            self._scan_for_property_paths_and_parameters(analyzed_expression, se.left)
            self._scan_for_property_paths_and_parameters(analyzed_expression, se.right)

        if not analyzed_expression.properties:
            raise InvalidExpressionError('There must be at least one property path. It is prone to query injection.')

        self._analyzed_map = analyzed_expression

        return self._analyzed_map

    def _scan_for_property_paths_and_parameters(self, analyzed_expression, sub_expression_part):
        """ Search for all property paths and parameters.
        """
        # Search for all referred property paths.
        if sub_expression_part.kind == ExpressionType.IS_PROPERTY_PATH:
            property_path = sub_expression_part.original

            analyzed_expression.properties[property_path] = None

        # Search for all referred property paths.
        if sub_expression_part.kind == ExpressionType.IS_PARAMETER:
            parameter_name = sub_expression_part.original[1:]

            analyzed_expression.parameters.append(parameter_name)

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
            expr.left = self._parse_side(expr.left)
        except InvalidExpressionError as exception:
            raise InvalidExpressionError('The left side of the expression cannot be parsed.')

        try:
            expr.right  = self._parse_side(expr.right)
        except InvalidExpressionError as exception:
            raise InvalidExpressionError('The left side of the expression cannot be parsed.')

        # Validate the syntax on the fixed syntaxes.
        if expr.operand in fixed_syntax_operands:
            if expr.left.kind != ExpressionType.IS_PROPERTY_PATH:
                raise InvalidExpressionError('The property path must be on the left of the operand.')

            if expr.right.kind == ExpressionType.IS_PROPERTY_PATH:
                raise InvalidExpressionError('The property path cannot be on the right of the operand.')

        # If the left side refers to the root path but not for the index search,
        # the method will raise the invalid expression error.
        if expr.left.kind == ExpressionType.IS_PROPERTY_PATH \
            and '.' not in expr.left.original \
            and expr.operand != ExpressionOperand.OP_INDEX_SEARCH:
            raise InvalidExpressionError('The property path to the root entity can only be used by index search.')

        # The property path must be in the expression.
        if expr.left.kind != ExpressionType.IS_PROPERTY_PATH and expr.right.kind != ExpressionType.IS_PROPERTY_PATH:
            raise InvalidExpressionError('The property path must be in the expression.')

        return expr

    def _parse_side(self, sub_statement):
        kind = ExpressionType.IS_DATA

        if self._re_parameter.match(sub_statement):
            kind = ExpressionType.IS_PARAMETER

        elif self._re_property_path.match(sub_statement) or self._re_root_path.match(sub_statement):
            kind = ExpressionType.IS_PROPERTY_PATH

        if kind != ExpressionType.IS_DATA:
            alias = self._re_property_path_delimiter.split(sub_statement)[0]\
                if self._re_property_path_delimiter.search(sub_statement) \
                else sub_statement[1:]

            return self._create_expression_part({
                'original': sub_statement,
                'kind':     kind,
                'value':    None,
                'alias':    alias
            })

        decoded_data = None

        try:
            decoded_data = json.loads(sub_statement)
        except ValueError as exception:
            raise InvalidExpressionError('Unable to decode the data.')

        return self._create_expression_part({
            'original': sub_statement,
            'kind':     kind,
            'value':    decoded_data,
            'alias':    None
        })

    def _create_expression_part(self, parameters):
        return ExpressionPart(**parameters)

    def _parse(self, statement):
        matches = self._re_statement.match(statement)

        if not matches:
            raise InvalidExpressionError('Incomplete statement: {}'.format(statement))

        raw_expr   = matches.groupdict()
        expression = Expression(**raw_expr)

        return expression