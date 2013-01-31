from pymongo import Connection

class Database(object):
    """ MongoDB Database

    :param name: the name of the database
    :type  name: str
    :param connection: the database connection
    :type  connection: pymongo.Connection

    .. warning::

        This class is obsolete after Tori 2.0.

    """
    def __init__(self, name, connection=None):
        self._connection = connection
        self._name       = name
        self._database   = None

    def collection(self, name):
        # Assign the default connection if not provided.
        if not self._connection:
            self._connection = Connection()

        if not self._database:
            self._database = self._connection[self._name]

        return self._database[name]