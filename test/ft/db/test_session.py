from ft.db.dbtestcase import DbTestCase
from passerine.db.common import ProxyObject
from passerine.db.uow import Record
from passerine.db.entity import entity
from passerine.db.mapper import link, CascadingType, AssociationType

@link('left', association=AssociationType.ONE_TO_ONE, cascading=[CascadingType.PERSIST, CascadingType.DELETE])
@link('right', association=AssociationType.ONE_TO_ONE, cascading=[CascadingType.PERSIST, CascadingType.DELETE])
@entity
class TestNode(object):
    def __init__(self, name, left, right):
        self.name  = name
        self.left  = left
        self.right = right

    def __repr__(self):
        return '<TestNode {} "{}">'.format(self.id, self.name)

@entity
class Computer(object):
    def __init__(self, name):
        self.name = name

@link('computer', Computer, association=AssociationType.ONE_TO_ONE)
@link('delegates', association=AssociationType.ONE_TO_MANY, cascading=[CascadingType.PERSIST, CascadingType.DELETE])
@entity
class Developer(object):
    def __init__(self, name, computer=None, delegates=[]):
        self.name      = name
        self.computer  = computer
        self.delegates = delegates

class TestFunctional(DbTestCase):
    def test_commit_with_insert_with_cascading(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.session.repository(TestNode)
        doc        = self._find_one_by_name(TestNode, 'a')

        self.assertEqual(len(reference_map), len(collection.filter()))
        self.assertEqual(reference_map['a'].id, doc.id)

    def test_commit_with_insert_without_cascading(self):
        reference_map = self.__mock_data_without_cascading()

        developer_collection = self.session.repository(Developer)
        computer_collection  = self.session.repository(Computer)

        self.session.persist(reference_map['d1'])
        self.session.flush()

        developers = self._get_all(Developer)
        computers  = self._get_all(Computer)

        self.assertEqual(1, len(developers))
        self.assertEqual(0, len(computers))

        developer = self._find_one_by_name(Developer, 'Shiroyuki')

        self.assertIsNone(developer.computer.id)

        raw_data = developer_collection.driver.find_one(
            developer_collection.name,
            {'_id': developer.id}
        )

        self.assertIsNone(raw_data['computer'])

    def test_commit_with_update(self):
        reference_map = self.__inject_data_with_cascading()

        doc = self.session.repository(TestNode).filter_one({'name': 'a'})
        doc.name = 'root'

        self.session.persist(doc)
        self.session.flush()

        docs = self.session.repository(TestNode).filter()

        self.assertEqual(len(reference_map), len(docs))
        self.assertEqual(reference_map['a'].id, doc.id)
        self.assertEqual(reference_map['a'].name, doc.name)

        doc = self.session.repository(TestNode).filter_one({'name': 'root'})

        self.assertEqual(reference_map['a'].id, doc.id)

    def test_commit_with_update_with_cascading(self):
        reference_map = self.__inject_data_with_cascading()

        doc = self.session.repository(TestNode).filter_one({'name': 'a'})
        doc.left.name = 'left'

        self.session.persist(doc)
        self.session.flush()

        docs = self.session.repository(TestNode).filter()

        self.assertEqual(len(reference_map), len(docs))
        self.assertEqual(reference_map['b'].id, doc.left.id)
        self.assertEqual(reference_map['b'].name, doc.left.name)

        doc = self.session.repository(TestNode).filter_one({'name': 'a'})

        self.assertEqual(reference_map['b'].id, doc.left.id)

    def test_commit_with_update_without_cascading(self):
        reference_map = self.__mock_data_without_cascading()

        developer_collection = self.session.repository(Developer)
        computer_collection = self.session.repository(Computer)

        self.session.persist(reference_map['d1'], reference_map['c1'])
        self.session.flush()

        self.assertEqual(1, len(developer_collection.filter()))
        self.assertEqual(1, len(computer_collection.filter()))

        developer = developer_collection.filter_one({'name': 'Shiroyuki'})
        developer.computer.name = 'MacBook Pro'

        self.session.persist(developer)
        self.session.flush()

        record = self.session._uow.retrieve_record(developer.computer)

        self.assertEqual(Record.STATUS_CLEAN, record.status)

        raw_data = computer_collection.driver.find_one(
            computer_collection.name,
            {'_id': reference_map['c1'].id}
        )

        self.assertNotEqual(raw_data['name'], developer.computer.name)

    def test_commit_with_delete(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.session.repository(TestNode)
        doc_g      = collection.filter_one({'name': 'g'})

        self.session.delete(doc_g)
        self.session.flush()

        self.assertEqual(len(reference_map) - 1, len(collection.filter()))

    def test_commit_with_delete_with_cascading(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.session.repository(TestNode)
        doc_a      = collection.filter_one({'name': 'a'})

        self.session.delete(doc_a)
        self.session.flush()

        self.assertEqual(len(reference_map) - 4, len(collection.filter()))

    def test_commit_with_delete_with_cascading_with_some_dependency_left(self):
        reference_map     = self.__inject_data_with_cascading()
        expected_max_size = len(reference_map) + 1

        collection = self.session.repository(TestNode)

        # Added an extra node that relies on node "f" without using the collection.
        collection.driver.insert(
            collection.name,
            {'left': None, 'right': reference_map['f'].id, 'name': 'extra'}
        )

        doc_h = collection.filter_one({'name': 'h'})

        self.session.delete(doc_h)
        self.session.flush()

        self.assertEqual(
            expected_max_size - 1,
            len(collection.filter()),
            'Expected for %s nodes remaining' % expected_max_size
        )

    def test_commit_with_delete_with_cascading_with_some_unsupervised_dependency_left(self):
        reference_map     = self.__inject_data_with_cascading()
        expected_max_size = len(reference_map) + 1

        collection = self.session.repository(TestNode)

        # Added an extra node that relies on node "f" without using the repository.
        collection.driver.insert(
            collection.name,
            {'left': None, 'right': reference_map['f'].id, 'name': 'extra'}
        )

        self.session.delete(reference_map['e'], reference_map['h'])
        self.session.flush()

        remainings = collection.filter()

        self.assertEqual(
            expected_max_size - 2,
            len(remainings),
            ', '.join([d.name for d in remainings])
        )

    def test_commit_with_delete_with_cascading_with_no_dependency_left(self):
        reference_map = self.__inject_data_with_cascading()

        collection = self.session.repository(TestNode)

        self.session.delete(reference_map['e'], reference_map['h'])
        self.session.flush()

        self.assertEqual(len(reference_map) - 3, len(collection.filter()))

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

        self.session.persist(reference_map['a'], reference_map['e'], reference_map['g'], reference_map['h'])
        self.session.flush()

        return reference_map

    def __mock_data_without_cascading(self):
        reference_map = {}

        reference_map['c1'] = Computer('MacBook Air')
        reference_map['d1'] = Developer('Shiroyuki', reference_map['c1'])

        return reference_map