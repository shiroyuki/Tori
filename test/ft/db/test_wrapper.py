import unittest
from sqlalchemy import Column, Integer, String
from tori.db.wrapper import Entity, Repository

class Dummy(Entity):
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
        db = Repository()
        db.reflect()

        session = db.session

        a = Dummy(name='a')
        b = Dummy(name='b')

        db.post(a, b)
