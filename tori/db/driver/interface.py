class QueryIteration(object):
    """ Driver Query Iteration

        :param alias: the alias of the rewritten target
        :type  alias: str
        :param native_query: the native query for a specific engine
    """
    def __init__(self, alias, native_query):
        self.alias = alias
        self.native_query = native_query

class QuerySequence(object):
    """ Driver Query Sequence """
    def __init__(self):
        self._iterations = []

    def add(self, iteration):
        self._iterations.append(iteration)

    def each(self):
        for iteration in self._iterations:
            yield iteration

class DriverInterface(object):
    def __init__(self, config, dialect):
        self._config = config
        self._client = None
        self._database_name = None
        self._dialect = dialect

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def dialect(self):
        return self._dialect

    @dialect.setter
    def dialect(self, value):
        self._dialect = value

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def database_name(self):
        return self._database_name

    @database_name.setter
    def database_name(self, database_name):
        self._database_name = database_name

    def db(self, name): raise NotImplemented()

    def collection(self, name): raise NotImplemented()

    def insert(self, collection_name, data): raise NotImplemented()

    def connect(self, config): raise NotImplemented()

    def disconnect(self): raise NotImplemented()

    def indice(self): raise NotImplemented()

    def index_count(self): raise NotImplemented()