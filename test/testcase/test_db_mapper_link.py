import unittest
from pymongo import Connection
from tori.db.session import Session
from tori.db.repository import Repository
from tori.db.common import ProxyObject
from tori.db.entity   import entity
from tori.db.manager    import Manager
from tori.db.mapper     import AssociationType, link

@entity('s')
class Skill(object):
    def __init__(self, name):
        self.name = name

#@link('skills', Skill, None, AssociationType.ONE_TO_MANY)
@entity('j')
class Job(object):
    def __init__(self, name, level, skills=[]):
        self.name   = name
        self.level  = level
        self.skills = skills

@entity('w')
class Weapon(object):
    def __init__(self, name, attack, defend):
        self.name   = name
        self.attack = attack
        self.defend = defend

@link('job', Job, association=AssociationType.ONE_TO_ONE)
@link('left_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@link('right_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@entity('c')
class Character(object):
    def __init__(self, name, level, job, left_hand, right_hand, _id=None):
        self._id   = _id
        self.name  = name
        self.level = level
        self.job   = job
        self.left_hand  = left_hand
        self.right_hand = right_hand

class TestDbMapperLink(unittest.TestCase):
    connection       = Connection()
    registered_types = {
        'c': Character,
        'w': Weapon,
        'j': Job,
        's': Skill
    }

    ts_character = {
        '_id':   1,
        'name':  'Shiroyuki',
        'level': 82,
        'job':   1,
        'left_hand':  2,
        'right_hand': 1
    }

    ts_job = {
        '_id':    1,
        'name':   'Knight',
        'level':  8,
        'skills': [
            {'name': 'Attack'},
            {'name': 'Charge'}
        ]
    }

    ts_shield = {
        '_id':    2,
        'name':   'Shield',
        'attack': 76,
        'defend': 234
    }

    ts_sword = {
        '_id':    1,
        'name':   'Sword',
        'attack': 495,
        'defend': 89
    }

    def setUp(self):
        self.session = Session(0, self.connection['test_tori_db_mapper_link'], self.registered_types)

        for collection in self.session.collections:
            collection._api.remove() # Reset the database

        self.session.collection(Character)._api.insert(self.ts_character)
        self.session.collection(Job)._api.insert(self.ts_job)
        self.session.collection(Weapon)._api.insert(self.ts_shield)
        self.session.collection(Weapon)._api.insert(self.ts_sword)

    def tearDown(self):
        pass

    def test_get(self):
        character = self.session.collection(Character).filter_one()

        self.assertEqual('Shiroyuki', character.name)
        self.assertIsInstance(character.job, ProxyObject) # Check the type of the proxy object
        self.assertIsInstance(character.job._actual, Job) # Check the type of the actual object
        self.assertEqual(1, character.job.id) # Check if the property of the actual object is accessible via the proxy
        self.assertEqual('Knight', character.job.name) # Check if the property of the actual object is accessible via the proxy
        self.assertFalse(character.job._read_only) # Check if the proxy setting is readable
