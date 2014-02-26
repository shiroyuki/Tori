from ft.db.dbtestcase import DbTestCase
from tori.db.session import Session
from tori.db.entity import entity
from tori.db.manager import Manager
from tori.db.exception import UOWRepeatedRegistrationError, UOWUnknownRecordError
from tori.db.uow import Record

@entity
class TestClass(object):
    def __init__(self):
        self.a = 1
        self.b = 2

class TestFunctional(DbTestCase):
    def setUp(self):
        super(TestFunctional, self).setUp()

        self.uow = self.session._uow

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

        self.assertEqual(Record.STATUS_DIRTY, record.status)

    def test_dirty_with_existing_data_and_no_changes(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        test_object.a = 3

        del test_object.b

        self.uow.register_dirty(test_object)

        record     = self.uow.retrieve_record(test_object)
        change_set = self.uow._compute_change_set(record)

        self.assertEqual(Record.STATUS_DIRTY, record.status)
        self.assertTrue('$set' in change_set)
        self.assertTrue('$unset' in change_set)
        self.assertFalse('$push' in change_set)

    def test_clean_with_existing_data(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_CLEAN, record.status)

    def test_delete_new_data(self):
        test_object = TestClass()

        self.uow.register_new(test_object)
        self.uow.register_deleted(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(record.status, Record.STATUS_IGNORED)

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
