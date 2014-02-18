class DriverInterface(object):
    def __init__(self):
        self._client = None
        self._database_name = None

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