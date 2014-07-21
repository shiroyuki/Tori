import re
from pymongo import MongoClient
from tori.db.driver.interface import DriverInterface, QueryIteration, QuerySequence
from tori.db.entity import Index
from tori.db.expression import Criteria, ExpressionOperand, ExpressionType, InvalidExpressionError as InvalidExpressionErrorBase
from tori.db.metadata.helper import EntityMetadataHelper

class InvalidExpressionError(InvalidExpressionErrorBase):
    """ MongoDB-specific Invalid Expression Error """

class UnsupportedExpressionError(InvalidExpressionErrorBase):
    """ MongoDB-specific Unsupported Expression Error

        This is due to that the expression may be unsafe (e.g., 1 = 2) or result
        in unnecessary complex computation (e.g., e.mobile_phone = e.home_phone).
    """

class Dialect(object):
    _OP_IN = '$in'
    _operand_map = {}

    def __init__(self):
        self._regex_ppath_delimiter = re.compile('\.')

    def get_native_operand(self, generic_operand):
        if not self._operand_map:
            self._operand_map.update({
                ExpressionOperand.OP_EQ: None,
                ExpressionOperand.OP_NE: '$ne',
                ExpressionOperand.OP_GE: '$gte',
                ExpressionOperand.OP_GT: '$gt',
                ExpressionOperand.OP_LE: '$lte',
                ExpressionOperand.OP_LT: '$lt',
                ExpressionOperand.OP_IN: self._OP_IN,
                ExpressionOperand.OP_NOT_IN: '$nin',
                ExpressionOperand.OP_SQL_LIKE: '$regex'
            })

        if generic_operand not in self._operand_map:
            raise RuntimeError('{} operand is not supported for this engine.')

        return self._operand_map[generic_operand]

    def get_alias_to_native_query_map(self, query):
        expression_set = query.criteria.get_analyzed_version()
        alias_to_conditions_map = {}

        # Process the non-join conditions
        for expression in expression_set.expressions:
            operand = self.get_native_operand(expression.operand)
            left    = expression.left
            right   = expression.right

            if expression.left.kind == expression.right.kind:
                raise UnsupportedExpressionError('The given criteria contains an expression whose both sides of expression are of the same type (e.g., property path, primitive value and parameter). Unfortunately, the expression is not supported by the backend datastore.')

            # Re-reference the pointers (to improve the readability).
            property_side  = None
            constrain_side = None

            if expression.left.kind == ExpressionType.IS_PROPERTY_PATH:
                property_side  = expression.left
                constrain_side = expression.right
            else:
                property_side  = expression.right
                constrain_side = expression.left

            alias = property_side.alias

            property_path   = ''.join(self._regex_ppath_delimiter.split(property_side.original)[1:])
            constrain_value = constrain_side.value

            if constrain_side.kind == ExpressionType.IS_PARAMETER:
                parameter_name  = constrain_side.alias
                constrain_value = query.definition_map[parameter_name]

            if alias not in alias_to_conditions_map:
                alias_to_conditions_map[alias] = {}

            native_query = {
                property_path: constrain_value
            }

            if operand:
                native_query = {
                    property_path: {
                        operand: constrain_value
                    }
                }

            alias_to_conditions_map[alias].update(native_query)

        # Handling the join conditions
        for alias in alias_to_conditions_map:
            join_config = query.join_map[alias]

            if not join_config['result_list']:
                continue

            parent_alias = join_config['parent_alias']

            # "No parent alias" indicates that this is not a join query. Ignore the rest.
            if not parent_alias:
                continue

            joined_keys = [document['_id'] for document in join_config['result_list']]

            current_native_query = alias_to_conditions_map[alias]
            parent_native_query  = alias_to_conditions_map[join_config['parent_alias']]

            parent_native_query[join_config['property_path']] = {
                self._OP_IN: joined_keys
            }

        return alias_to_conditions_map

    def get_iterating_constrains(self, query):
        option_map = {}

        if query._force_loading:
            option_map['_force_loading'] = query._force_loading # applicable only to MongoDB

        if query._order_by:
            option_map['sort'] = query._order_by

        if query._offset and query._offset > 0:
            option_map['skip'] = self._offset

        if query._limit and query._limit > 0:
            option_map['limit'] = query._limit

        return option_map

class Driver(DriverInterface):
    def __init__(self, config, dialect = Dialect()):
        super(Driver, self).__init__(config, dialect)

        if isinstance(self.config, dict):
            if 'name' not in self.config:
                raise ValueError('Please specify the name of the database.')

            self.database_name = self.config['name']

            del self.config['name']

            return

        # "config" is an URL.
        matches = re.search('^mongodb://[^/]+/(?P<database_name>[^\?]+)', config)

        if not matches:
            raise ValueError('Please specify the name of the database.')

        self.database_name = matches.groupdict()['database_name']

    def connect(self):
        if self.client:
            return

        if isinstance(self.config, dict):
            self.client = MongoClient(**self.config) # as a config map

            return

        self.client = MongoClient(config) # as an URL

    def disconnect(self):
        self.client.disconnect()

        self.client = None

    def db(self, name=None):
        return self.client[name or self.database_name]

    def collections(self):
        return self.db().collections

    def collection(self, name):
        return self.db()[name]

    def insert(self, collection_name, data):
        api = self.collection(collection_name)
        return api.insert(data)

    def update(self, collection_name, criteria, new):
        api = self.collection(collection_name)
        return api.update(criteria, new)

    def remove(self, collection_name, criteria):
        api = self.collection(collection_name)
        return api.remove(criteria)

    def find_one(self, collection_name, criteria, fields=None):
        api = self.collection(collection_name)

        if fields:
            return api.find_one(criteria, fields)

        return api.find_one(criteria)

    def find(self, collection_name, criteria, fields=None):
        """ Find the data sets with the native API.

            :param collection_name: the name of the collection
            :param criteria: the criteria compatible with the native API.
            :param fields: the list of required fields.
        """
        api = self.collection(collection_name)

        if fields:
            return api.find(criteria, fields)

        return api.find(criteria)

    def query(self, metadata, query, iterating_constrains):
        """ Find the data sets with :class:`tori.db.query.Criteria`.

            :param metadata: the metadata of the target collection / repository
            :type  metadata: tori.db.metadata.entity.EntityMetadata
            :param query: the native query
            :param iterating_constrains: the iterating constrains
        """

        collection_name = metadata.collection_name
        force_loading   = iterating_constrains['_force_loading'] if '_force_loading' in iterating_constrains else False

        cursor = self.find(collection_name, query)

        if not force_loading and 'limit' in iterating_constrains and iterating_constrains['limit'] != 1:
            cursor = self.find(collection_name, query, fields=[])

        for constrain in iterating_constrains:
            if '_' == constrain[0]:
                continue

            cursor.__getattribute__(constrain)(iterating_constrains[constrain])

        return [data for data in cursor]

    def indice(self):
        return [index for index in self.collection('system.indexes').find()]

    # MongoDB-specific operation
    def ensure_index(self, collection_name, index, force_index):
        options = {
            'background': (not force_index)
        }

        order_list = index.to_list() if isinstance(index, Index) else index

        if isinstance(order_list, list):
            indexed_field_list = ['{}_{}'.format(field, order) for field, order in order_list]
            indexed_field_list.sort()
            options['index_identifier'] = '-'.join(indexed_field_list)

        self.collection(collection_name).ensure_index(order_list, **options)

    def drop(self, collection_name):
        self.collection(collection_name).drop()

    def drop_indexes(self, collection_name):
        self.collection(collection_name).drop_indexes()

    def index_count(self):
        return self.total_row_count('system.indexes')

    def total_row_count(self, collection_name):
        return self.collection(collection_name).count()