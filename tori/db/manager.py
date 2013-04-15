from pymongo import Connection
from bson.objectid import ObjectId
from tori.db.session import Session

class Manager(object):
    def __init__(self, name, connection=None, document_types=[]):
        """Entity Manager

        :param name: the name of the database
        :type  name: str
        :param connection: the connection object
        :type  connection: pymongo.Connection
        :param document_types: the list of document classes/types
        :type  document_types: list
        """
        self._name             = name
        self._connection       = connection or Connection()
        self._database         = self._connection[self._name]
        self._session_map      = {}
        self._registered_types = {}

        for document_type in document_types:
            self._registered_types[document_type.__collection_name__] = document_type

    @property
    def db(self):
        """ Database-level API

        :rtype: pymongo.database.Database

        .. warning::

            Please use this property with caution. The unit of work cannot track any changes done by direct calls via
            this property and may mess up with the change-set calculation.

        """
        return self._database

    def open_session(self, id=None, supervised=False):
        if not supervised:
            return Session(0, self.db, self._registered_types)

        if not id:
            id = ObjectId()

        if id in self._session_map:
            return self._session_map[id]

        session = Session(id, self.db, self._registered_types)

        if supervised:
            self._session_map[id] = session

        return session

    def close_session(self, id_or_session):
        id = id_or_session.id if isinstance(id_or_session, Session) else id_or_session

        if not id or id not in self._session_map:
            return

        del self._session_map[id]
