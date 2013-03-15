from unittest import TestCase
from pymongo import Connection
from tori.db.session import Session
from tori.db.common import ProxyObject
from tori.db.uow import Record

try:
    from unittest.mock import Mock, MagicMock # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock # Python 2.7

from tori.db.entity import entity
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType, AssociationType

@entity('members')
class Member(object):
    def __init__(self, name):
        self.name = name

@link(
    mapped_by='members',
    target=Member,
    association=AssociationType.MANY_TO_MANY,
    cascading=[CascadingType.DELETE, CascadingType.PERSIST]
)
@entity('groups')
class Group(object):
    def __init__(self, name, members=[]):
        self.name    = name
        self.members = members

class TestDbUowAssociationManyToMany(TestCase):
    connection       = Connection()
    registered_types = {
        'groups':  Group,
        'members': Member
    }

    def setUp(self):
        self.session = Session(0, self.connection['test_tori_db_session_assoc_m2m'], self.registered_types)

        for collection in self.session.collections:
            collection._api.remove() # Reset the database

        self.session.db['groups_members'].remove({}) # Reset the associations

        self.__set_fixtures()

    def _test_load(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        group_a  = groups.filter_one({'name': 'group a'})
        member_d = members.filter_one({'name': 'member d'})

        self.assertTrue(group_a.members._loaded, 'The IDs should be loaded by UOW.')
        self.assertEqual(2, len(group_a.members))
        self.assertTrue(group_a.members._loaded)
        self.assertEqual('member a', group_a.members[0].name)
        self.assertEqual('member b', group_a.members[1].name)

    def test_commit(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        associations = self.session.collection(Group.__relational_map__['members'].association_class.cls)

        group_a  = groups.filter_one({'name': 'group a'})
        group_b  = groups.filter_one({'name': 'group b'})
        group_c  = groups.filter_one({'name': 'group c'})
        member_d = members.filter_one({'name': 'member d'})

        groups.delete(group_c)

        group_a.members.append(member_d)
        group_b.members.append(member_d)

        group_a.members.pop(0)

        self.session.persist(group_a, group_b)
        self.session.flush()

        self.assertEqual(2, groups._api.count())
        self.assertEqual(5, associations._api.count())

    def _test_commit_with_new_element_on_explicit_persistence(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        associations = self.session.collection(Group.__relational_map__['members'].association_class.cls)

        group_a  = groups.filter_one({'name': 'group a'})
        group_b  = groups.filter_one({'name': 'group b'})
        group_c  = groups.filter_one({'name': 'group c'})
        member_d = members.filter_one({'name': 'member d'})

        member_d.name = 'extra member'

        member_e = members.new(name='member e')

        groups.delete(group_c)

        group_a.members.append(member_d)
        group_b.members.append(member_e)

        group_a.members.pop(0)

        self.session.flush()

        self.assertEqual(2, groups._api.count())
        self.assertEqual(5, associations._api.count())

    def __set_fixtures(self):
        data_sets = {
            'members': [
                {'name': 'member a'},
                {'name': 'member b'},
                {'name': 'member c'},
                {'name': 'member d'}
            ],
            'groups': [
                {'name': 'group a'},
                {'name': 'group b'},
                {'name': 'group c'}
            ]
        }

        associations = [
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 2),
            (2, 0),
            (2, 2)
        ]

        api = self.session.collection(Member)._api

        for data in data_sets['members']:
            object_id   = api.insert(data)
            data['_id'] = object_id

        api = self.session.collection(Group)._api

        for data in data_sets['groups']:
            object_id   = api.insert(data)
            data['_id'] = object_id

        api = self.session.db['378900d37908d31ef2aa5a12c1a8443d612719e9ac8ef2625dee448c']

        api.remove()

        for origin, destination in associations:
            api.insert({
                'origin':      data_sets['groups'][origin]['_id'],
                'destination': data_sets['members'][destination]['_id']
            })

        collection_names = self.session.db.collection_names()

        self.assertIn('members', collection_names)
        self.assertIn('groups', collection_names)
        self.assertIn('378900d37908d31ef2aa5a12c1a8443d612719e9ac8ef2625dee448c', collection_names)