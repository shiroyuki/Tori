from unittest import TestCase
from tori.db.uow import Record

try:
    from unittest.mock import Mock, MagicMock # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock # Python 2.7

from tori.db.document import document
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType, AssociationType


@link('left', association_type=AssociationType.ONE_TO_ONE, cascading_options=[CascadingType.PERSIST, CascadingType.DELETE])
@link('right', association_type=AssociationType.ONE_TO_ONE, cascading_options=[CascadingType.PERSIST, CascadingType.DELETE])
@document
class TestNode(object):
    def __init__(self, name, left, right):
        self.name  = name
        self.left  = left
        self.right = right

    def __repr__(self):
        return '<TestNode {} "{}">'.format(self.id, self.name)

@document
class Computer(object):
    def __init__(self, name):
        self.name = name

@link('computer', Computer, association_type=AssociationType.ONE_TO_ONE)
@link('friends', association_type=AssociationType.ONE_TO_MANY)
@document
class Developer(object):
    def __init__(self, name, computer, friends=[]):
        self.name     = name
        self.computer = computer
        self.friends  = friends

class TestDbManager(TestCase):
    def setUp(self):
        self.em  = Manager('tori_test', document_types=[Developer, Computer, TestNode])

        for collection in self.em.collections:
            collection._api.remove() # Reset the database

    def test_commit_with_insert_with_cascading(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.em.collection(TestNode)
        doc        = collection.filter_one({'name': 'a'})

        self.assertEqual(len(reference_map), len(collection.filter()))
        self.assertEqual(reference_map['a'].id, doc.id)

    def test_commit_with_insert_without_cascading(self):
        reference_map = self.__mock_data_without_cascading()

        developer_collection = self.em.collection(Developer)
        computer_collection = self.em.collection(Computer)

        self.em.persist(reference_map['d1'])
        self.em.flush()

        self.assertEqual(1, len(developer_collection.filter()))
        self.assertEqual(0, len(computer_collection.filter()))

        developer = developer_collection.filter_one({'name': 'Shiroyuki'})

        self.assertIsNone(developer.computer.id)

        raw_data = developer_collection._api.find_one({'_id': developer.id})

        self.assertIsNone(raw_data['computer'])

    def test_commit_with_update(self):
        reference_map = self.__inject_data_with_cascading()

        doc = self.em.collection(TestNode).filter_one({'name': 'a'})
        doc.name = 'root'

        self.em.persist(doc)
        self.em.flush()

        docs = self.em.collection(TestNode).filter()

        self.assertEqual(len(reference_map), len(docs))
        self.assertEqual(reference_map['a'].id, doc.id)
        self.assertEqual(reference_map['a'].name, doc.name)

        doc = self.em.collection(TestNode).filter_one({'name': 'root'})

        self.assertEqual(reference_map['a'].id, doc.id)

    def test_commit_with_update_with_cascading(self):
        reference_map = self.__inject_data_with_cascading()

        doc = self.em.collection(TestNode).filter_one({'name': 'a'})
        doc.left.name = 'left'

        self.em.persist(doc)
        self.em.flush()

        docs = self.em.collection(TestNode).filter()

        self.assertEqual(len(reference_map), len(docs))
        self.assertEqual(reference_map['b'].id, doc.left.id)
        self.assertEqual(reference_map['b'].name, doc.left.name)

        doc = self.em.collection(TestNode).filter_one({'name': 'a'})

        self.assertEqual(reference_map['b'].id, doc.left.id)

    def test_commit_with_update_without_cascading(self):
        reference_map = self.__mock_data_without_cascading()

        developer_collection = self.em.collection(Developer)
        computer_collection = self.em.collection(Computer)

        self.em.persist(reference_map['d1'], reference_map['c1'])
        self.em.flush()

        self.assertEqual(1, len(developer_collection.filter()))
        self.assertEqual(1, len(computer_collection.filter()))

        developer = developer_collection.filter_one({'name': 'Shiroyuki'})
        developer.computer.name = 'MacBook Pro'

        self.em.persist(developer)
        self.em.flush()

        record = self.em._uow.retrieve_record(developer.computer)

        self.assertEqual(Record.STATUS_CLEAN, record.status)

        raw_data = computer_collection._api.find_one({'_id': reference_map['c1'].id})

        self.assertNotEqual(raw_data['name'], developer.computer.name)

    def test_commit_with_delete(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.em.collection(TestNode)
        doc_g      = collection.filter_one({'name': 'g'})

        self.em.delete(doc_g)
        self.em.flush()

        self.assertEqual(len(reference_map) - 1, len(collection.filter()))

    def test_commit_with_delete_with_cascading(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.em.collection(TestNode)
        doc_a      = collection.filter_one({'name': 'a'})

        self.em.delete(doc_a)
        self.em.flush()

        self.assertEqual(len(reference_map) - 4, len(collection.filter()))

    def test_commit_with_delete_with_cascading_with_some_dependency_left(self):
        reference_map     = self.__inject_data_with_cascading()
        expected_max_size = len(reference_map) + 1

        collection = self.em.collection(TestNode)

        # Added an extra node that relies on node "f" without using the collection.
        collection._api.insert({'left': None, 'right': reference_map['f'].id, 'name': 'extra'})

        doc_h = collection.filter_one({'name': 'h'})

        self.em.delete(doc_h)
        self.em.flush()

        self.assertEqual(
            expected_max_size - 1,
            len(collection.filter()),
            'Expected for %s nodes remaining' % expected_max_size
        )

    def test_commit_with_delete_with_cascading_with_some_unsupervised_dependency_left(self):
        reference_map     = self.__inject_data_with_cascading()
        expected_max_size = len(reference_map) + 1

        collection = self.em.collection(TestNode)

        # Added an extra node that relies on node "f" without using the collection.
        collection._api.insert({'left': None, 'right': reference_map['f'].id, 'name': 'extra'})

        self.em.delete(reference_map['e'], reference_map['h'])
        self.em.flush()

        self.assertEqual(
            expected_max_size - 2,
            len(collection.filter()),
            'Expected for %s nodes remaining' % (expected_max_size - 2)
        )

    def test_commit_with_delete_with_cascading_with_no_dependency_left(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.em.collection(TestNode)

        self.em.delete(reference_map['e'], reference_map['h'])
        self.em.flush()

        self.assertEqual(len(reference_map) - 3, len(collection.filter()))

    def __debug_graph(self, graph):
        print('----- Begin -----')

        for id in graph:
            node = graph[id]

            print('[{} {} {}]'.format(node.record.entity.name, node.score, node.record.entity.id))

            for other in node.adjacent_nodes:
                print('  --> [{} {} {}]'.format(other.record.entity.name, other.score, node.record.entity.id))

            for other in node.reverse_edges:
                print('  <-- [{} {} {}]'.format(other.record.entity.name, other.score, node.record.entity.id))
        print('----- End -----')

    def __inject_data_with_cascading(self):
        reference_map = {}

        reference_map['g'] = TestNode('g', None, None)
        reference_map['f'] = TestNode('f', None, None)
        reference_map['e'] = TestNode('e', None, reference_map['f'])
        reference_map['d'] = TestNode('d', None, None)
        reference_map['c'] = TestNode('c', reference_map['d'], None)
        reference_map['b'] = TestNode('b', None, reference_map['d'])
        reference_map['a'] = TestNode('a', reference_map['b'], reference_map['c'])
        reference_map['h'] = TestNode('h', reference_map['f'], None)

        self.em.persist(reference_map['a'], reference_map['e'], reference_map['g'], reference_map['h'])
        self.em.flush()

        return reference_map

    def __mock_data_without_cascading(self):
        reference_map = {}

        reference_map['c1'] = Computer('MacBook Air')
        reference_map['d1'] = Developer('Shiroyuki', reference_map['c1'])

        return reference_map