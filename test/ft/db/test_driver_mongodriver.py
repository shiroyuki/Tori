from ft.db.dbtestcase   import DbTestCase, skip
from tori.db.session    import Session
from tori.db.repository import Repository
from tori.db.common     import ProxyObject
from tori.db.entity     import entity
from tori.db.manager    import Manager
from tori.db.mapper     import AssociationType, link

@entity('skills')
class Skill(object):
    def __init__(self, name):
        self.name = name

@link('skills', Skill, None, AssociationType.ONE_TO_MANY)
@entity('jobs')
class Job(object):
    def __init__(self, name, level, skills=[]):
        self.name   = name
        self.level  = level
        self.skills = skills

@entity('tools')
class Weapon(object):
    def __init__(self, name, attack, defend):
        self.name   = name
        self.attack = attack
        self.defend = defend

@link('skills', Skill, None, AssociationType.ONE_TO_MANY)
@link('job', Job, association=AssociationType.ONE_TO_ONE)
@link('left_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@link('right_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@entity('characters')
class Character(object):
    def __init__(self, name, level, job, left_hand, right_hand, skills, _id=None):
        self._id   = _id
        self.name  = name
        self.level = level
        self.job   = job
        self.left_hand  = left_hand
        self.right_hand = right_hand
        self.skills = skills

class TestFunctional(DbTestCase):
    verify_data = True

    #@skip('Under development')
    def test_simple_query_ok(self):
        self._reset_db(self.__data_provider())

        repo = self.session.repository(Character)

        query = repo.new_criteria('c')
        query.join('c.skills', 's')
        query.join('c.job', 'j')
        query.join('j.skills', 'j_k')
        query.join('c.left_hand', 'l')

        query.expect('j.name = :job')
        query.expect('c.level < 50')
        query.expect('s.name = "Attack"')
        query.expect('j_k.name = "Charge"')
        query.expect('l.attack > :min_attack')

        query.define('job', 'Knight')
        query.define('min_attack', 400)

        query.limit(1)

        character = repo.find(query)

        self.assertIsInstance(character, Character, 'This is a single query.')

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
                        'right_hand': 1,
                        'skills': [
                            2
                        ]
                    },
                    {
                        '_id':   2,
                        'name':  'Cloud',
                        'level': 12,
                        'job':   1,
                        'left_hand':  1,
                        'right_hand': 2,
                        'skills': [
                            1
                        ]
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
                            1, 2
                        ]
                    }
                ]
            },
            {
                'class': Skill,
                'fixtures': [
                    {
                        '_id':  1,
                        'name': 'Attack'
                    },
                    {
                        '_id':  2,
                        'name': 'Charge'
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