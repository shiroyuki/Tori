from unittest import TestCase
from tori.db.common import ProxyObject
from tori.db.uow import Record

try:
    from unittest.mock import Mock, MagicMock # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock # Python 2.7

from tori.db.document import document
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType, AssociationType

@document('members')
class Member(object):
    def __init__(self, name):
        self.name = name

@link(
    mapped_by='members',
    target=Member,
    association=AssociationType.MANY_TO_MANY,
    cascading=[CascadingType.DELETE, CascadingType.PERSIST]
)
@document('groups')
class Group(object):
    def __init__(self, name, members=[]):
        self.name    = name
        self.members = members

class TestDbManagerAssociationManyToMany(TestCase):
    def setUp(self):
        self.em  = Manager('tori_test', document_types=[Group, Member])

        for collection in self.em.collections:
            collection._api.remove() # Reset the database

        self.em.db['groups_members'].remove({}) # Reset the associations

        self.__set_fixtures()

    def test_load(self):
        collection = self.em.collection(Group)

        group_a = collection.filter_one({'name': 'group a'})

        self.assertEqual(2, len(group_a.members))
        self.assertEqual('member a', group_a.members[0].name)
        self.assertEqual('member b', group_a.members[1].name)

    def __set_fixtures(self):
        data_sets = {
            'members': [
                {'name': 'member a'},
                {'name': 'member b'},
                {'name': 'member c'}
            ],
            'groups': [
                {'name': 'group a'},
                {'name': 'group b'}
            ]
        }

        associations = [
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 2)
        ]

        api = self.em.collection(Member)._api

        for data in data_sets['members']:
            object_id   = api.insert(data)
            data['_id'] = object_id

        self.assertEqual(3, api.count())

        api = self.em.collection(Group)._api

        for data in data_sets['groups']:
            object_id   = api.insert(data)
            data['_id'] = object_id

        self.assertEqual(2, api.count())

        api = self.em.db['groups_members']

        for origin, destination in associations:
            api.insert({
                'from': data_sets['groups'][origin]['_id'],
                'to':   data_sets['members'][destination]['_id']
            })

        self.assertEqual(4, api.count())

        collection_names = self.em.db.collection_names()

        self.assertIn('members', collection_names)
        self.assertIn('groups', collection_names)
        self.assertIn('groups_members', collection_names)