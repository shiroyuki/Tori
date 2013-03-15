from unittest import TestCase
from pymongo import Connection
from tori.db.session import Session
from tori.db.common import ProxyObject
from tori.db.uow import Record
from tori.db.entity import entity
from tori.db.mapper import link, CascadingType, AssociationType

@entity('test_db_uow_ass_one_to_many_computer')
class Computer(object):
    def __init__(self, name):
        self.name = name

@link('computer', Computer, association=AssociationType.ONE_TO_ONE)
@link('delegates', association=AssociationType.ONE_TO_MANY, cascading=[CascadingType.PERSIST, CascadingType.DELETE])
@entity('test_db_uow_ass_one_to_many_developer')
class Developer(object):
    def __init__(self, name, computer=None, delegates=[]):
        self.name      = name
        self.computer  = computer
        self.delegates = delegates

class TestDbUowAssociationOneToMany(TestCase):
    connection = Connection()

    def setUp(self):
        self.session = Session(0, self.connection['test_tori_db_session'])

        for collection in self.session.collections:
            collection._api.remove() # Reset the database

        self.__inject_data_with_one_to_many_association()

    def test_fetching(self):
        c = self.session.collection(Developer)

        boss = c.filter_one({'name': 'boss'})

        self.assertIsInstance(boss.delegates, list)

        self.assertIsInstance(boss.delegates[0], ProxyObject)
        self.assertEqual(boss.delegates[0].name, 'a')
        self.assertIsInstance(boss.delegates[1], ProxyObject)
        self.assertEqual(boss.delegates[1].name, 'b')

    def test_cascading_on_persist(self):
        c = self.session.collection(Developer)

        boss = c.filter_one({'name': 'boss'})
        boss.delegates[0].name = 'assistant'

        self.session.persist(boss)
        self.session.flush()

        data = c._api.find_one({'_id': boss.delegates[0].id})

        self.assertEqual(boss.delegates[0].name, data['name'])

    def test_update_association(self):
        c = self.session.collection(Developer)

        boss = c.filter_one({'name': 'boss'})
        boss.delegates[0].name = 'assistant'

        boss.delegates.append(Developer('c'))

        self.session.persist(boss)
        self.session.flush()

        data = c._api.find_one({'name': 'c'})

        self.assertIsNotNone(data)
        self.assertEqual(boss.delegates[2].id, data['_id'])

        data = c._api.find_one({'name': 'boss'})

        self.assertEqual(3, len(data['delegates']))

        for delegate in boss.delegates:
            self.assertIn(delegate.id, data['delegates'])

    def test_cascading_on_delete_with_some_deps(self):
        c = self.session.collection(Developer)

        boss = c.filter_one({'name': 'boss'})
        boss.delegates[0].name = 'assistant'

        boss.delegates.append(Developer('c'))

        self.session.persist(boss)

        architect = Developer('architect', delegates=[boss.delegates[0]])

        self.session.persist(architect)
        self.session.flush()

        self.assertEqual(5, len(c.filter()))

        self.session.delete(architect)
        self.session.flush()

        self.assertEqual(4, len(c.filter()), 'should have some dependencies left (but no orphan node)')

    def test_cascading_on_delete_with_no_deps(self):
        c = self.session.collection(Developer)

        boss = c.filter_one({'name': 'boss'})

        print('point a')

        for d in c._api.find():
            print(d)

        boss.delegates[0].name = 'assistant'

        boss.delegates.append(Developer('c'))

        self.session.persist(boss)

        print('point b')

        for d in c._api.find():
            print(d)

        architect = Developer('architect', delegates=[boss.delegates[0]])

        self.session.persist(architect)
        self.session.flush()

        print('point c')

        for d in c._api.find():
            print(d)

        self.session.delete(architect)
        self.session.delete(boss)
        self.session.flush()

        count = len(c.filter())

        print('point d')

        for d in c._api.find():
            print(d)

        self.assertEqual(0, count, 'There should not exist dependencies left (orphan removal). (remaining: {})'.format(count))

    def __inject_data_with_one_to_many_association(self):
        api = self.session.collection(Developer)._api

        api.remove()

        a_id = api.insert({'name': 'a'})
        b_id = api.insert({'name': 'b'})

        api.insert({'name': 'boss', 'delegates': [a_id, b_id]})