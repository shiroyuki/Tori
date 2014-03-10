from unittest import TestCase, skip
from pymongo import Connection
from tori.db.driver.mongodriver import Driver
from tori.db.session import Session

class DbTestCase(TestCase):
    verify_data = False
    connection = Connection() # used for setup-cleanup operation
    default_collection_name = 't3test'
    session = None
    driver = None

    def open_driver(self):
        self.driver = Driver({'name': self.default_collection_name})
        self.driver.connect()

    def close_driver(self):
        del self.driver

    def setUp(self):
        self._setUp()

    def _setUp(self):
        self.connection.drop_database(self.default_collection_name)
        self.open_driver()
        self.session = Session(self.driver)

    def tearDown(self):
        if not self.verify_data:
            self.connection.drop_database(self.default_collection_name)

        self.close_driver()

        del self.session

    def _reset_db(self, data_set):
        for data in data_set:
            cls  = data['class']
            repo = self.session.repository(cls)

            self.driver.drop_indexes(repo.name)
            self.driver.drop(repo.name)

            repo.setup_index()

            for fixture in data['fixtures']:
                self.driver.insert(repo.name, fixture)

            if self.verify_data:
                for fixture in self.driver.find(repo.name, {}):
                    print('{}: {}'.format(repo.name, fixture))