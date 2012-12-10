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

        self._collections[key] = None
