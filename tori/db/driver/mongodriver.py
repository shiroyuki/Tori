import re
from pymongo import MongoClient
from tori.db.entity import Index
from tori.db.expression import Expression, InvalidExpressionError as InvalidExpressionErrorBase
from tori.db.driver.interface import DriverInterface

class InvalidExpressionError(InvalidExpressionErrorBase):
    """ MongoDB-specific Invalid Expression Error """

class Driver(DriverInterface):
    def __init__(self, config):
        super(Driver, self).__init__(config)

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

    def query(self, criteria):
        """ Find the data sets with :class:`tori.db.criteria.Criteria`.

            :param criteria: the criteria
            :type  criteria: tori.db.criteria.Criteria
        """
        collection_name = criteria.origin.__collection_name__
        force_loading   = criteria._force_loading
        auto_index      = criteria._auto_index

        condition = self._convert_expression_to_condition(
                collection_name, criteria.expression
            ) \
            if criteria.expression \
            else criteria._condition # To be removed in Tori 3.1+

        cursor = self.find(collection_name, condition)

        if not force_loading and criteria._limit != 1:
            cursor = self.find(collection_name, criteria._condition, fields=[])

        if auto_index and not criteria._indexed:
            if criteria._indexed_target_list:
                for field in criteria._indexed_target_list:
                    self.ensure_index(collection_name, field, False)

            if auto_index and not criteria._indexed:
                self.ensure_index(collection_name, criteria._order_by, False)

            criteria._indexed = True

        if criteria._order_by:
            cursor.sort(criteria._order_by)

        if criteria._offset and criteria._offset > 0:
            cursor.skip(self._offset)

        if criteria._limit and criteria._limit > 0:
            cursor.limit(criteria._limit)

        return [data for data in cursor]

    def _convert_expression_to_condition(self, collection_name, expression):
        api   = self.collection(collection_name)

        pass

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