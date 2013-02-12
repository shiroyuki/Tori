from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock # Python 2.7

from pymongo.collection import Collection

from tori.db.document import document
from tori.db.manager import Manager
from tori.db.mapper import link, CascadingType
from tori.db.exception import UOWRepeatedRegistrationError, UOWUnknownRecordError
from tori.db.uow import UnitOfWork, Record

@link('left', cascading_options=[CascadingType.PERSIST, CascadingType.DELETE])
@link('right', cascading_options=[CascadingType.PERSIST, CascadingType.DELETE])
@document
class TestNode(object):
    def __init__(self, name, left, right):
        self.name  = name
        self.left  = left
        self.right = right

    def __repr__(self):
        return '<TestNode {} "{}">'.format(self.id, self.name)

@document
class TestClass(object):
    def __init__(self):
        self.a = 1
        self.b = 2

class TestDbManagerAndUnitOfWork(TestCase):
    def setUp(self):
        self.em  = Manager('tori_test', document_types=[TestNode])
        self.uow = UnitOfWork(self.em)

        for collection in self.em.collections():
            collection._api.remove() # Reset the database

    def test_new(self):
        test_object = TestClass()

        self.uow.register_new(test_object)

        self.assertTrue(self.uow.has_record(test_object))

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_NEW, record.status)

    def test_dirty_with_new_data(self):
        test_object = TestClass()

        self.uow.register_new(test_object)
        self.uow.register_dirty(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_NEW, record.status)

    def test_dirty_with_existing_data_and_some_changes(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)
        self.uow.register_dirty(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_CLEAN, record.status)

    def test_dirty_with_existing_data_and_no_changes(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        test_object.a = 3

        del test_object.b

        self.uow.register_dirty(test_object)

        record     = self.uow.retrieve_record(test_object)
        change_set = self.uow.compute_change_set(record)

        self.assertEqual(Record.STATUS_DIRTY, record.status)
        self.assertTrue('$set' in change_set)
        self.assertTrue('$unset' in change_set)
        self.assertFalse('$push' in change_set)

    def test_clean_with_existing_data(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_CLEAN, record.status)

    def test_delete_with_new_data(self):
        test_object = TestClass()

        self.uow.register_new(test_object)
        self.uow.register_deleted(test_object)

        self.assertRaises(UOWUnknownRecordError, self.uow.retrieve_record, (test_object))

    def test_delete_with_existing_data(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)
        self.uow.register_deleted(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_DELETED, record.status)

    def test_exception_on_new_to_new_repeated_registration(self):
        test_object = TestClass()

        self.uow.register_new(test_object)

        self.assertRaises(UOWRepeatedRegistrationError, self.uow.register_new, test_object)

    def test_exception_on_new_to_clean_repeated_registration(self):
        test_object = TestClass()

        self.uow.register_new(test_object)

        self.assertRaises(UOWRepeatedRegistrationError, self.uow.register_clean, test_object)

    def test_exception_on_clean_to_new_repeated_registration(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        self.assertRaises(UOWRepeatedRegistrationError, self.uow.register_new, test_object)

    def test_exception_on_clean_to_clean_repeated_registration(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        self.assertRaises(UOWRepeatedRegistrationError, self.uow.register_clean, test_object)

    def test_exception_on_record_retrieval(self):
        test_object = TestClass()

        self.assertRaises(UOWUnknownRecordError, self.uow.retrieve_record, test_object)

    def test_commit_with_insert(self):
        reference_map = self.__inject_data()

        collection = self.em.collection(TestNode)
        doc        = collection.filter_one({'name': 'a'})

        self.assertEqual(7, len(collection.filter()))
        self.assertEqual(reference_map['a'].id, doc.id)

    def test_commit_with_update(self):
        reference_map = self.__inject_data()

        doc = self.em.collection(TestNode).filter_one({'name': 'a'})

        self.em.persist(doc)
        self.em.flush()

        docs = self.em.collection(TestNode).filter()

        self.assertEqual(7, len(docs))
        self.assertEqual(reference_map['a'].id, doc.id)
        self.assertEqual(reference_map['a'].name, doc.name)

    def test_commit_with_delete(self):
        self.__inject_data()

        collection = self.em.collection(TestNode)
        doc_g      = collection.filter_one({'name': 'g'})

        self.em.delete(doc_g)
        self.em.flush()

        self.assertEqual(6, len(collection.filter()))

    # Test for change_set calculation
    def test_change_set(self):
        pass

    def __inject_data(self):
        reference_map = {}

        reference_map['g'] = TestNode('g', None, None)
        reference_map['f'] = TestNode('f', None, None)
        reference_map['e'] = TestNode('e', None, reference_map['f'])
        reference_map['d'] = TestNode('d', None, None)
        reference_map['c'] = TestNode('c', reference_map['d'], None)
        reference_map['b'] = TestNode('b', None, reference_map['d'])
        reference_map['a'] = TestNode('a', reference_map['b'], reference_map['c'])

        self.em.persist(reference_map['a'], reference_map['e'], reference_map['g'])

        commit_order = self.em._uow.compute_order()
        name_order   = []

        for dnode in commit_order:
            lookup_key = self.em._uow._convert_object_id_to_str(dnode.object_id)
            uid        = self.em._uow._object_id_map[lookup_key]
            record     = self.em._uow._record_map[uid]

            name_order.append(record.entity.name)

        self.em.flush()

        return reference_map