class Manager(object):
    def __init__(self, database):
        """Constructor

        :type database: tori.db.database.Database
        """
        self._database = database

    @property
    def database(self):
        """Database

        :rtype: tori.db.database.Database
        """
        return self._database