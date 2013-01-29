from tori.db.common import PseudoObjectId
from tori.db.collection import Collection
from tori.db.uow import UnitOfWork

class Manager(object):
    def __init__(self, database):
        """Constructor

        :type database: tori.db.database.Database
        """
        self._database    = database
        self._collections = {}
        self._uow         = UnitOfWork(self)

    @property
    def database(self):
        """Database

        :rtype: tori.db.database.Database
        """
        return self._database

    def collection(self, document_class):
        """Retrieve the collection

        :param document_class: the class of document/entity
        :type  document_class: object
        :rtype: tori.db.collection.Collection
        """
        key = hash(document_class)

        if key not in self._collections:
            return None

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
