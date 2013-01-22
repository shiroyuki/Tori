from tori.db.exception import UOWRepeatedRegistrationError, UOWUpdateError, UOWUnknownRecordError
from tori.decorator.common import singleton
from tori.db.common import GuidGenerator

class Record(object):
    STATUS_CLEAN     = 1
    STATUS_DELETED   = 2
    STATUS_DIRTY     = 3
    STATUS_NEW       = 4
    STATUS_CANCELLED = 0

    def __init__(self, entity, status):
        self.entity = entity
        self.status = status

@singleton
class UnitOfWork(object):
    def __init__(self):
        self._generator  = GuidGenerator()
        self._record_map = {}

    def register_new(self, entity):
        uid = self._retrieve_entity_guid(entity)

        if self.has_record(entity):
            raise UOWRepeatedRegistrationError('Could not mark the entity as new.')

        self._record_map[uid] = Record(entity, Record.STATUS_NEW)

    def register_dirty(self, entity):
        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_DELETED:
            raise UOWUpdateError('Could not update the deleted entity.')

        if record.status == Record.STATUS_NEW:
            return

        record.status = Record.STATUS_DIRTY

    def register_clean(self, entity):
        uid = self._retrieve_entity_guid(entity)

        if uid in self._record_map:
            raise UOWRepeatedRegistrationError('Could not mark the entity as clean')

        self._record_map[uid] = Record(entity, Record.STATUS_CLEAN)

    def register_deleted(self, entity):
        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_NEW:
            record.status = Record.STATUS_CANCELLED

            return

        record.status = Record.STATUS_DELETED

    def commit(self):
        pass

    def retrieve_record(self, entity):
        uid = self._retrieve_entity_guid(entity)

        if uid not in self._record_map:
            raise UOWUnknownRecordError('Unable to retrieve the record for this entity.')

        return self._record_map[uid]

    def has_record(self, entity):
        return self._retrieve_entity_guid(entity) in self._record_map

    def _retrieve_entity_guid(self, entity):
        return hash(entity)
