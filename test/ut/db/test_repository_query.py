from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock, patch # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock, patch # Python 2.7

from bson import ObjectId
from passerine.db.entity import entity
from passerine.db.repository import Repository
from passerine.db.mapper import link, CascadingType, AssociationType

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

class TestUnit(TestCase):
    def setUp(self):
        pass

    @patch('passerine.db.session.Session')
    def test_positive_post(self, session):
        repository = Repository(session, Member)
        query      = repository.new_criteria()
        criteria   = query.new_criteria()
