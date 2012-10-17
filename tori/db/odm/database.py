from pymongo import Connection

class Database(object):
    def __init__(self, name, connection=None):
        self._connection = connection
        self._name       = name
        self._database   = None

    def collection(self, name):
        # Assign the default connection if not provided.
        if not self._connection:
            self._connection = Connection()

        if not self._database:
            self._database = self._connection[name]

        return self._database[name]