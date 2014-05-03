from ft.db.dbtestcase import DbTestCase
from tori.db.session import Session
from tori.db.common import ProxyObject
from tori.db.uow import Record
from tori.db.entity import entity
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType, AssociationType
from tori.db.metadata.helper import EntityMetadataHelper

@link(
    mapped_by='groups',
    inverted_by='members',
    target='ft.db.test_issue_27.Group',
    association=AssociationType.MANY_TO_MANY
)
@entity('members')
class Member(object):
    def __init__(self, name, groups=[]):
        self.name = name
        self.groups = groups

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

class TestFunctional(DbTestCase):
    def setUp(self):
        self._setUp()
        self._reset_db(self.__data_provider())
        self.__reset_associations()

    def test_load(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        group_a  = groups.filter_one({'name': 'group a'})
        member_d = members.filter_one({'name': 'member d'})

        self.assertTrue(group_a.members._loaded, 'The IDs should be loaded by UOW.')
        self.assertEqual(2, len(group_a.members))
        self.assertEqual(2, len(group_a.members[0].groups))
        self.assertEqual(0, len(member_d.groups))
        self.assertTrue(group_a.members._loaded)
        self.assertEqual('member a', group_a.members[0].name)
        self.assertEqual('member b', group_a.members[1].name)

    def test_with_new_entites(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        associations = self.__association_to_members()

        group = groups.new(name='From Up On Poppy Hill')

        umi   = members.new(name='Umi')
        shun  = members.new(name='Shun')
        shiro = members.new(name='Shiro')

        group.members.extend([umi, shun, shiro])

        groups.post(group)

        self.assertEqual(4, len(groups))
        self.assertEqual(7, len(members))
        self.assertEqual(9, len(associations))

    def test_commit(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        associations = self.__association_to_members()

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

        self.assertEqual(2, len(groups))
        self.assertEqual(5, len(associations))

    def test_commit_with_new_element_on_explicit_persistence_and_repository(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        associations = self.__association_to_members()

        group_a  = groups.filter_one({'name': 'group a'})
        group_b  = groups.filter_one({'name': 'group b'})
        group_c  = groups.filter_one({'name': 'group c'})
        member_d = members.filter_one({'name': 'member d'})

        member_d.name = 'extra member'

        member_e = members.new(name='member e')

        groups.delete(group_c)

        group_a.members.append(member_d)
        group_a.members.pop(0)
        groups.put(group_a)

        group_b.members.append(member_e)
        groups.put(group_b)

        self.assertEqual(2, len(groups))
        self.assertEqual(5, len(associations))

    def test_commit_with_new_element_on_explicit_persistence_and_session(self):
        groups  = self.session.collection(Group)
        members = self.session.collection(Member)

        associations = self.__association_to_members()

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

        self.session.persist(group_a)
        self.session.persist(group_b)
        self.session.flush()

        self.assertEqual(2, len(groups))
        self.assertEqual(5, len(associations))

    def __association_to_members(self):
        return self.session.collection(EntityMetadataHelper.extract(Group).relational_map['members'].association_class.cls)

    def __data_provider(self):
        return [
            {
                'class': Member,
                'fixtures': [
                    {'_id': 1, 'name': 'member a'},
                    {'_id': 2, 'name': 'member b'},
                    {'_id': 3, 'name': 'member c'},
                    {'_id': 4, 'name': 'member d'}
                ]
            },
            {
                'class': Group,
                'fixtures': [
                    {'_id': 1, 'name': 'group a'},
                    {'_id': 2, 'name': 'group b'},
                    {'_id': 3, 'name': 'group c'}
                ]
            }
        ]

    def __reset_associations(self):
        associations = [
            (1, 1),
            (1, 2),
            (2, 2),
            (2, 3),
            (3, 1),
            (3, 3)
        ]

        api = self.driver.collection('groups_members')

        api.remove()

        for origin, destination in associations:
            api.insert({
                'origin':      origin,
                'destination': destination
            })