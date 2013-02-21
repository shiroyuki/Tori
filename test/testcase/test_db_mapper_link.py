import unittest
from tori.db.collection import Collection
from tori.db.common import ProxyObject
from tori.db.document   import document
from tori.db.manager    import Manager
from tori.db.mapper     import AssociationType, link

@document('s')
class Skill(object):
    def __init__(self, name):
        self.name = name

#@link('skills', Skill, None, AssociationType.ONE_TO_MANY)
@document('j')
class Job(object):
    def __init__(self, name, level, skills=[]):
        self.name   = name
        self.level  = level
        self.skills = skills

@document('w')
class Weapon(object):
    def __init__(self, name, attack, defend):
        self.name   = name
        self.attack = attack
        self.defend = defend

@link('job', Job, association=AssociationType.ONE_TO_ONE)
@link('left_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@link('right_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@document('c')
class Character(object):
    def __init__(self, name, level, job, left_hand, right_hand, _id=None):
        self._id   = _id
        self.name  = name
        self.level = level
        self.job   = job
        self.left_hand  = left_hand
        self.right_hand = right_hand

class TestDbMapperLink(unittest.TestCase):
    em = 1

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
        self.em = Manager('tori_test', document_types=[Skill, Job, Weapon, Character, Skill])

        for collection in self.em.collections:
            collection._api.remove() # Reset the database

        self.em.collection(Character)._api.insert(self.ts_character)
        self.em.collection(Job)._api.insert(self.ts_job)
        self.em.collection(Weapon)._api.insert(self.ts_shield)
        self.em.collection(Weapon)._api.insert(self.ts_sword)

    def tearDown(self):
        pass

    def test_get(self):
        character = self.em.collection(Character).filter_one()

        self.assertEqual('Shiroyuki', character.name)
        self.assertIsInstance(character.job, ProxyObject) # Check the type of the proxy object
        self.assertIsInstance(character.job._actual, Job) # Check the type of the actual object
        self.assertEqual(1, character.job.id) # Check if the property of the actual object is accessible via the proxy
        self.assertEqual('Knight', character.job.name) # Check if the property of the actual object is accessible via the proxy
        self.assertFalse(character.job._read_only) # Check if the proxy setting is readable



