import unittest

from sqlalchemy import Column, Integer, String

from tori.db.entity  import Entity as BaseEntity
from tori.db.repository import DatabaseRepository as RDB

class Dummy(BaseEntity):
    __tablename__ = 'dummy'

    id   = Column(Integer, primary_key=True)
    name = Column(String)

class TestDb(unittest.TestCase):
    """ Test DB APIs """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_assembly(self):
        db = RDB()
        db.reflect()

        session = db.session

        a = Dummy(name='a')
        b = Dummy(name='b')

        db.post(a, b)
