from pymongo import Connection
from tori.db.collection import Collection
from tori.db.uow import UnitOfWork

class Manager(object):
    def __init__(self, name, connection=None, document_types=[]):
        """Constructor

        :param name: the name of the database
        :type  name: str
        :param connection: the database connection
        :type  connection: pymongo.Connection
        """
        self._uow  = UnitOfWork(self)
        self._name = name
        self._connection  = connection or Connection()
        self._database    = self._connection[self._name]
        self._collections = {}
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

    def collections(self):
        return [self.collection(self._registered_types[key]) for key in self._registered_types]

    def collection(self, document_class):
        """Retrieve the collection

        :param document_class: the class of document/entity
        :type  document_class: type

        :rtype: tori.db.collection.Collection
        """
        key = document_class.__collection_name__

        if key not in self._registered_types:
            return None

        if key not in self._collections:
            self._collections[key] = Collection(self, self._database[key], self._registered_types[key])

        return self._collections[key]

    def delete(self, *entities):
        for entity in entities:
            self._uow.register_deleted(entity)

    def persist(self, *entities):
        for entity in entities:
            if entity.id:
                self._uow.register_dirty(entity)

                continue

            self._uow.register_new(entity)

    def flush(self):
        self._uow.commit()

    def register(self, document_class):
        key = hash(document_class)

        if key in self._collections:
            return

        self._collections[key] = Collection(self.database, document_class)

    def register_multiple(self, *document_classes):
        for document_class in document_classes:
            self.register(document_class)

    def _get_class_key(self, entity):
        return hash(entity.__class__)
