import unittest
from tori.db.exception import UOWRepeatedRegistrationError, UOWUnknownRecordError
from tori.db.uow import UnitOfWork, Record

class TestClass(object): pass

class TestDbUow(unittest.TestCase):
    def setUp(self):
        self.uow = UnitOfWork()

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

    def test_dirty_with_existing_data(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)
        self.uow.register_dirty(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_DIRTY, record.status)

    def test_clean_with_existing_data(self):
        test_object = TestClass()

        self.uow.register_clean(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_CLEAN, record.status)

    def test_delete_with_new_data(self):
        test_object = TestClass()

        self.uow.register_new(test_object)
        self.uow.register_deleted(test_object)

        record = self.uow.retrieve_record(test_object)

        self.assertEqual(Record.STATUS_CANCELLED, record.status)

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