import re
from pymongo import MongoClient
from tori.db.driver.interface import DriverInterface
from tori.db.entity import Index
from tori.db.expression import Criteria, InvalidExpressionError as InvalidExpressionErrorBase
from tori.db.metadata.helper import EntityMetadataHelper

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

    def query(self, query):
        """ Find the data sets with :class:`tori.db.query.Criteria`.

            :param query: the query
            :type  query: tori.db.query.Criteria
        """
        # 2014.06.30:
        # This method is subject to rewrite as the driver should be straight
        # forward and contain no complicate logic.
        metadata_origin = EntityMetadataHelper.extract(query.origin)

        collection_name = metadata_origin.collection_name
        force_loading   = query._force_loading
        auto_index      = query._auto_index

        condition = self._convert_native_query(query) \
            if query.is_new_style \
            else query._condition # To be removed in Tori 3.1+

        cursor = self.find(collection_name, condition)

        if not force_loading and query._limit != 1:
            cursor = self.find(collection_name, query._condition, fields=[])

        if auto_index and not query._indexed:
            if query._indexed_target_list:
                for field in query._indexed_target_list:
                    self.ensure_index(collection_name, field, False)

            if auto_index and not query._indexed:
                self.ensure_index(collection_name, query._order_by, False)

            query._indexed = True

        if query._order_by:
            cursor.sort(query._order_by)

        if query._offset and query._offset > 0:
            cursor.skip(self._offset)

        if query._limit and query._limit > 0:
            cursor.limit(query._limit)

        return [data for data in cursor]

    def _convert_native_query(self, query):
        expression_set = query.criteria.get_analyzed_version()

        import pprint
        pp = pprint.PrettyPrinter(indent=2)

        pp.pprint(query.join_map)
        pp.pprint(query.definition_map)
        pp.pprint(expression_set.in_json)

        for expression in expression_set.expressions:
            pass

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