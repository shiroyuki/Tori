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
    def __init__(self, left, right):
        self.left = left
        self.right = right

@document
class TestClass(object):
    def __init__(self):
        self.a = 1
        self.b = 2

class TestDbUow(TestCase):
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

    # Test for commit
    def test_commit_normal_path(self):
        a = TestClass() # new -> commit as new
        b = TestClass() # new -> update -> commit as new
        c = TestClass() # new -> delete -> no commit
        d = TestClass() # new -> update -> delete -> no commit
        e = TestClass() # clean -> no commit
        f = TestClass() # clean -> update -> commit as dirty
        g = TestClass() # clean -> delete -> commit as deleted
        h = TestClass() # clean -> update -> delete -> commit as deleted

        self.uow.register_new(a)

        self.uow.register_new(b)

        b.a = 3

        self.uow.register_dirty(b)

        self.uow.register_new(c)
        self.uow.register_deleted(c)

        self.uow.register_new(d)

        d.a = 4

        self.uow.register_deleted(d)

        self.uow.register_clean(e)

        self.uow.register_clean(f)

        f.a = 5

        self.uow.register_dirty(f)

        self.uow.register_clean(g)
        self.uow.register_deleted(g)

        self.uow.register_clean(h)

        h.a = 6

        self.uow.register_deleted(h)

        collection = Mock(Collection)

        collection.insert = Mock(return_value=5)

    def test_commit_with_post_only(self):
        g = TestNode(None, None)
        f = TestNode(None, None)
        e = TestNode(None, f)
        d = TestNode(None, None)
        c = TestNode(d, None)
        b = TestNode(None, d)
        a = TestNode(b, c)

        self.em.persist(a, e, g)

        order = self.em._uow.compute_order()

        print('a', a.id)
        print('b', b.id)
        print('c', c.id)
        print('d', d.id)
        print('e', e.id)
        print('f', f.id)
        print('g', g.id)

        for item in order:
            print(item)

        self.em.flush()

        nodes = self.em.collection(TestNode)._api.find()

        for node in nodes:
            print(node)

    # Test for change_set calculation
    def test_change_set(self):
        pass

