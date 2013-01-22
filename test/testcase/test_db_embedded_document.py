import unittest
from tori.db.exception import LockedIdException, ReservedAttributeException
from tori.db.collection import Collection
from tori.db.document   import document
from tori.db.database   import Database
from tori.db.mapper     import AssociationType, embed

@document
class Skill(object):
    def __init__(self, name):
        self.name = name

@document
@embed('skills', Skill, AssociationType.ONE_TO_MANY)
class Job(object):
    def __init__(self, name, level, skills=[]):
        self.name   = name
        self.level  = level
        self.skills = skills

@document
class Weapon(object):
    def __init__(self, name, attack, defend):
        self.name   = name
        self.attack = attack
        self.defend = defend

@document
@embed('job', Job)
@embed('left_hand', Weapon)
@embed('right_hand', Weapon)
class Character(object):
    def __init__(self, name, level, job, left_hand, right_hand, _id=None):
        self._id   = _id
        self.name  = name
        self.level = level
        self.job   = job
        self.left_hand  = left_hand
        self.right_hand = right_hand

class TestDbDocument(unittest.TestCase):
    db = Database('tori_test')
    collection = None

    test_stub = [
        {
            'name': 'Shiroyuki',
            'level': 82,
            'job': {
                'name':  'Knight',
                'level': 8,
                'skills': [
                    {'name': 'Attack'},
                    {'name': 'Charge'}
                ]
            },
            'left_hand': {
                'name':  'Shield',
                'attack': 76,
                'defend': 234
            },
            'right_hand': {
                'name':  'Sword',
                'attack': 495,
                'defend': 89
            }
        }
    ]

    test_attributes = {
        'name': 'Juti',
        'occupation': 'Developer'
    }

    def setUp(self):
        self.collection = Collection(
            self.db,
            Character,
            'test_orm_collection'
        )

        self.collection.delete_by_criteria()

        for data in self.test_stub:
            self.collection.api.insert(data)

    def tearDown(self):
        pass

    def test_changeset(self):
        character = self.collection.new_document(**self.test_stub[0])

        #print(character.get_changeset())

        character.reset_bits()

        #print(character.get_changeset())



    def test_create_document_with_dict(self):
        character = self.collection.new_document(**self.test_stub[0])

        self.assertIsInstance(character, Character)
        self.assertIsInstance(character.job, Job)
        self.assertIsInstance(character.left_hand, Weapon)
        self.assertIsInstance(character.right_hand, Weapon)

        self.assertEqual('Knight', character.job.name)
        self.assertEqual(2, len(character.job.skills))
        self.assertEqual('Attack', character.job.skills[0].name)
        self.assertEqual('Charge', character.job.skills[1].name)
        self.assertEqual('Shield', character.left_hand.name)
        self.assertEqual('Sword', character.right_hand.name)

    def test_create_document_with_object(self):
        character = self.collection.new_document(
            name='Kenshin',
            level=99,
            job=Job('Samurai', 10, [Skill('Attack'), Skill('Quick Draw')]),
            left_hand=None,
            right_hand=Weapon('Katana', 600, 0)
        )

        self.assertIsInstance(character, Character)
        self.assertIsInstance(character.job, Job)
        self.assertIsNone(character.left_hand)
        self.assertIsInstance(character.right_hand, Weapon)

        self.assertEqual('Katana', character.right_hand.name)

    def test_create_document_then_push_to(self):
        character = self.collection.new_document(
            name='Kenshin',
            level=99,
            job=Job('Samurai', 10, [Skill('Attack'), Skill('Quick Draw')]),
            left_hand=None,
            right_hand=Weapon('Katana', 600, 0)
        )

        self.assertIsInstance(character, Character)
        self.assertIsInstance(character.job, Job)
        self.assertIsNone(character.left_hand)
        self.assertIsInstance(character.right_hand, Weapon)

        self.assertEqual('Katana', character.right_hand.name)

    def test_fetch_embedded_document_from_collection(self):
        id = None

        for entity in self.collection.api.find():
            id = entity['_id']

        character = self.collection.get(id)

        self.assertIsInstance(character, Character)
        self.assertIsInstance(character.job, Job)
        self.assertIsInstance(character.left_hand, Weapon)
        self.assertIsInstance(character.right_hand, Weapon)

        self.assertEqual('Knight', character.job.name)
        self.assertEqual(2, len(character.job.skills))
        self.assertEqual('Attack', character.job.skills[0].name)
        self.assertEqual('Charge', character.job.skills[1].name)
        self.assertEqual('Shield', character.left_hand.name)
        self.assertEqual('Sword', character.right_hand.name)