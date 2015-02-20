from ft.db.dbtestcase import DbTestCase
from passerine.db.session import Session
from passerine.db.repository import Repository
from passerine.db.common import ProxyObject
from passerine.db.entity   import entity
from passerine.db.manager    import Manager
from passerine.db.mapper     import AssociationType, link

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

class TestFunctional(DbTestCase):
    def test_get(self):
        self._reset_db(self.__data_provider())

        character = self._get_first(Character)

        self.assertEqual('Shiroyuki', character.name)
        self.assertIsInstance(character.job, ProxyObject) # Check the type of the proxy object
        self.assertIsInstance(character.job._actual, Job) # Check the type of the actual object
        self.assertEqual(1, character.job.id) # Check if the property of the actual object is accessible via the proxy
        self.assertEqual('Knight', character.job.name) # Check if the property of the actual object is accessible via the proxy
        self.assertFalse(character.job._read_only) # Check if the proxy setting is readable

    def __data_provider(self):
        return [
            {
                'class': Character,
                'fixtures': [
                    {
                        '_id':   1,
                        'name':  'Shiroyuki',
                        'level': 82,
                        'job':   1,
                        'left_hand':  2,
                        'right_hand': 1
                    }
                ]
            },
            {
                'class': Job,
                'fixtures': [
                    {
                        '_id':    1,
                        'name':   'Knight',
                        'level':  8,
                        'skills': [
                            {'name': 'Attack'},
                            {'name': 'Charge'}
                        ]
                    }
                ]
            },
            {
                'class': Weapon,
                'fixtures': [
                    {
                        '_id':    2,
                        'name':   'Shield',
                        'attack': 76,
                        'defend': 234
                    },
                    {
                        '_id':    1,
                        'name':   'Sword',
                        'attack': 495,
                        'defend': 89
                    }
                ]
            }
        ]