from ft.db.dbtestcase   import DbTestCase, skip
from tori.db.session    import Session
from tori.db.repository import Repository
from tori.db.common     import ProxyObject
from tori.db.entity     import entity
from tori.db.manager    import Manager
from tori.db.mapper     import AssociationType, link

@entity('s')
class Skill(object):
    def __init__(self, name):
        self.name = name

@link('skills', Skill, None, AssociationType.ONE_TO_MANY)
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

@link('skills', Skill, None, AssociationType.ONE_TO_MANY)
@link('job', Job, association=AssociationType.ONE_TO_ONE)
@link('left_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@link('right_hand', Weapon, association=AssociationType.ONE_TO_ONE)
@entity('c')
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
    @skip('Under development')
    def test_simple_query_ok(self):
        self._reset_db(self.__data_provider())

        repo = self.session.repository(Character)

        criteria = repo.new_criteria('c')
        criteria.join('c.skills', 's')
        criteria.join('c.job', 'j')
        criteria.join('j.skills', 'j_k')
        criteria.join('c.left_hand', 'l')

        expression = criteria.new_expression()

        expression.expect('c.job < :job')
        expression.expect('c.level < 50')
        expression.expect('s.name = "Attack"')
        expression.expect('j_k.name = "Charge"')
        expression.expect('l.attack > :min_attack')

        criteria.define('job', 'Knight')
        criteria.define('min_attack', 400)

        criteria.expression = expression
        criteria.limit(1)

        character = repo.find(criteria)

        raise RuntimeError('Panda!')

        # todo: should use the same criteria as test_mapper_link

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