from unittest import TestCase

try:
    from unittest.mock import Mock, MagicMock # Python 3.3
except ImportError as exception:
    from mock import Mock, MagicMock # Python 2.7

from pymongo.collection import Collection

from tori.db.document import document
from tori.db.exception import UOWRepeatedRegistrationError, UOWUnknownRecordError
from tori.db.uow import UnitOfWork, Record

@document
class TestClass(object):
    def __init__(self):
        self.a = 1
        self.b = 2

class TestDbUow(TestCase):
    def setUp(self):
        self.uow = UnitOfWork(None)

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

    # Test for changeset calculation