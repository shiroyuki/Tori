from tori.db.collection import Collection

class Manager(object):
    def __init__(self, database):
        """Constructor

        :type database: tori.db.database.Database
        """
        self._database = database
        self._collections = {}

    @property
    def database(self):
        """Database

        :rtype: tori.db.database.Database
        """
        return self._database

    def register(self, document_class):
        key = str(document_class)

        if key in self._collections:
            return

        self._collections[key] = Collection(self.database, document_class)

    def register_multiple(self, *document_classes):
        for document_class in document_classes:
            self.register(document_class)

    def _get_class_key(self, entity):
        return str(entity.__class__)
