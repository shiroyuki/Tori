class QueryIteration(object):
    """ Driver Query Iteration

        This is a metadata class representing an iteration in complex queries.

        :param str  alias:        the alias of the rewritten target
        :param dict native_query: the native query for a specific engine

        .. note:: Internal use only
    """
    def __init__(self, alias, native_query):
        self.alias = alias
        self.native_query = native_query

class QuerySequence(object):
    """ Driver Query Sequence

        The collection represents the sequence of sub queries.
    """
    def __init__(self):
        self._iterations = []

    def add(self, iteration):
        """ Append the the iteration

            :param tori.db.driver.interface.QueryIteration iteration: the query iteration
        """
        self._iterations.append(iteration)

    def each(self):
        """ Get the sequence iterator.
        """
        for iteration in self._iterations:
            yield iteration

class DialectInterface(object):
    """ Dialect interface

        It is used to translate a generic query into a native query.
    """
    def get_native_operand(self, generic_operand):
        """ Translate a generic operand into a corresponding native operand.

            :param generic_operand: a generic operand

            :return: a native operand
            :rtype:  str
        """
        raise NotImplemented('Please define the operand transformation.')

    def get_alias_to_native_query_map(self, query):
        """ Retrieve a map from alias to native query.

            :param tori.db.criteria.Query: the query object
            :rtype: dict
        """
        expression_set = query.criteria.get_analyzed_version()
        alias_to_conditions_map = {}

        # Process the non-join conditions
        for expression in expression_set.expressions:
            operand = self.get_native_operand(expression.operand)
            left    = expression.left
            right   = expression.right

            self.process_non_join_conditions(
                alias_to_conditions_map,
                query.definition_map,
                left,
                right,
                operand
            )

        # Handling the join conditions
        for alias in alias_to_conditions_map:
            join_config = query.join_map[alias]

            if not join_config['result_list']:
                continue

            parent_alias = join_config['parent_alias']

            # "No parent alias" indicates that this is not a join query. Ignore the rest.
            if not parent_alias:
                continue

            self.process_join_conditions(
                alias_to_conditions_map,
                alias,
                join_config,
                parent_alias
            )

        return alias_to_conditions_map

    def get_iterating_constrains(self, query):
        """ Retrieve the query constrains.

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented('Define the native constrains.')

    def process_join_conditions(self, alias_to_conditions_map, alias, join_config, parent_alias):
        """ Process the join conditions.

            :param dict alias_to_conditions_map: a alias-to-conditions map
            :param dict join_config:             a join config map
            :param str  alias:                   an alias of the given join map
            :param str  parent_alias:            the parent alias of the given join map

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented('Generate a query without join conditions.')

    def process_non_join_conditions(self, alias_to_conditions_map, definition_map, left, right, operand):
        """ Process the non-join conditions.

            :param dict alias_to_conditions_map:            a alias-to-conditions map
            :param dict definition_map:                     a parameter-to-value map
            :param tori.db.expression.ExpressionPart left:  the left expression
            :param tori.db.expression.ExpressionPart right: the right expression
            :param operand:                                 the native operand

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented('Add join conditions.')


class DriverInterface(object):
    """ The abstract driver interface

        :param dict config: the configuration used to initialize the database connection / client
        :param tori.db.driver.interface.DialectInterface dialect: the corresponding dialect
    """
    def __init__(self, config, dialect):
        self._config = config
        self._client = None
        self._database_name = None
        self._dialect = dialect

    @property
    def config(self):
        """ Driver configuration """
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def dialect(self):
        """ Driver dialect """
        return self._dialect

    @dialect.setter
    def dialect(self, value):
        self._dialect = value

    @property
    def client(self):
        """ Driver Connection / Client """
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def database_name(self):
        """ The name of provisioned database """
        return self._database_name

    @database_name.setter
    def database_name(self, database_name):
        self._database_name = database_name

    def db(self, name):
        """ Low-level Database-class API

            :return: the low-level database-class API

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented()

    def collection(self, name):
        """ Low-level Collection-class API

            :return: the low-level collection-class API

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented()

    def insert(self, collection_name, data):
        """ Low-level insert function

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented()

    def connect(self, config):
        """ Connect the client to the server.

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented()

    def disconnect(self):
        """ Disconnect the client.

            :raise NotImplemented: only if the interface is not overridden.
        """
        raise NotImplemented()

    def indice(self):
        """ Retrieve the indice.

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented()

    def index_count(self):
        """ Retrieve the number of indexes.

            :raise NotImplemented: only if the interface is not overridden.
        """

        raise NotImplemented()