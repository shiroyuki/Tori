from tori.data.converter import ArrayConverter
from tori.db.exception import UOWRepeatedRegistrationError, UOWUpdateError, UOWUnknownRecordError
from tori.decorator.common import singleton

converter = ArrayConverter()
converter._max_depth = 0

class Record(object):
    STATUS_CLEAN     = 1
    STATUS_DELETED   = 2
    STATUS_DIRTY     = 3
    STATUS_NEW       = 4

    def __init__(self, entity, status):
        self.entity = entity
        self.status = status

        self.original_data_set = converter.convert(entity)

    @property
    def changeset(self):
        current_set = converter.convert(self.entity)

        if self.status == self.STATUS_NEW:
            return current_set
        elif self.status == self.STATUS_DELETED:
            return self.entity.id

        original_set = dict(self.original_data_set)

        change_set = {
            '$set':   {},
            '$push':  {}, # Ignored until the multiple-link association is implemented.
            '$unset': {}
        }

        original_property_set = set(original_set.keys())
        current_property_set  = set(current_set.keys())

        expected_property_list = original_property_set.intersection(current_property_set)
        expected_property_list = expected_property_list.union(current_property_set.difference(original_property_set))

        unexpected_property_list = original_property_set.difference(current_property_set)

        # Add or update properties
        for name in expected_property_list:
            if name in original_set and original_set[name] == current_set[name]:
                continue

            change_set['$set'][name] = current_set[name]

        # Remove unwanted properties
        for name in unexpected_property_list:
            change_set['$unset'][name] = 1

        directive_list = list(change_set.keys())

        # Clean up the change set
        for directive in directive_list:
            if change_set[directive]:
                continue

            del change_set[directive]

        return change_set

class UnitOfWork(object):
    """ Unit of Work

    This Unit of Work (UOW) is designed specifically for non-relational databases.

    .. note::

        It is the design decision to make sub-commit methods available so that when it is used with Imagination
        Framework, the other Imagination entity may intercept before or after actually committing data. In the other
        word, Imagination Framework acts as an event controller for any actions (public methods) of this class.

    """
    def __init__(self, entity_manager):
        self._em           = entity_manager
        self._record_map   = {} # Object Hash => Record
        self._id_map       = {} # Object ID (str) => Object Hash
        self._commit_order = [] # Object ID (BSON)

    def register_new(self, entity):
        uid = self._retrieve_entity_guid(entity)

        if self.has_record(entity):
            raise UOWRepeatedRegistrationError('Could not mark the entity as new.')

        self._record_map[uid] = Record(entity, Record.STATUS_NEW)

    def register_dirty(self, entity):
        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_DELETED:
            raise UOWUpdateError('Could not update the deleted entity.')

        if record.status == Record.STATUS_NEW or not record.changeset:
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
            self.delete_record(entity)

            return

        record.status = Record.STATUS_DELETED

    def commit(self):
        new_data_graph     = {}
        updated_data_graph = {}
        removal_data_graph = {}

        for uid in self._record_map:
            record = self._record_map[uid]

            collection_name = record.entity.__collection_name__

            if record.status == Record.STATUS_NEW:
                if collection_name not in new_data_graph:
                    new_data_graph[collection_name] = []

                new_data_graph[collection_name].append(record.changeset)
            elif record.status == Record.STATUS_DIRTY:
                updated_data_graph[collection_name][record.entity.id] = {
                    'old': record.original_data_set,
                    'new': record.changeset
                }
            elif record.status == Record.STATUS_DELETED:
                if collection_name not in removal_data_graph:
                    removal_data_graph[collection_name] = []

                removal_data_graph[collection_name].append(record.entity.id)

        self.commit_creations(new_data_graph)
        self.commit_updates(updated_data_graph)
        self.commit_removals(removal_data_graph)

    def commit_creations(self, data_graph):
        for collection_name in data_graph:
            self.commit_creations_for(collection_name, data_graph[collection_name])

    def commit_creations_for(self, collection_name, sub_data_graph):
        collection = self._em.db.collection(collection_name)

        for data_set in sub_data_graph:
            collection.insert(data_set, safe=True)

    def commit_updates(self, data_graph):
        for collection_name in data_graph:
            self._commit_updates_for(collection_name, data_graph[collection_name])

    def _commit_updates_for(self, collection_name, sub_data_graph):
        collection = self._em.db.collection(collection_name)

        for object_id in sub_data_graph:
            changeset = sub_data_graph[object_id]

            self.synchronize_update(
                collection,
                object_id,
                changeset['old'],
                changeset['new']
            )

    def commit_removals(self, data_graph):
        for collection_name in data_graph:
            self.commit_removals_for(collection_name, data_graph[collection_name])

    def commit_removals_for(self, collection_name, sub_data_graph):
        collection = self._em.collection(collection_name)

        for object_id in sub_data_graph:
            self.synchronize_delete(collection, object_id)

    def synchronize_new(self, collection, data_set):
        collection.insert(data_set)

    def synchronize_update(self, collection, object_id, old_data_set, new_data_set):
        """Synchronize the updated data

        :param collection: the target collection
        :param object_id: the object ID
        :param old_data_set: the original data (for event interception)
        :param new_data_set: the updated data
        """
        collection.update(
            {'_id': object_id},
            new_data_set,
            upsert=False
        )

    def synchronize_delete(self, collection, object_id):
        collection.remove({'_id': object_id})

    def retrieve_record(self, entity):
        uid = self._retrieve_entity_guid(entity)

        if uid not in self._record_map:
            raise UOWUnknownRecordError('Unable to retrieve the record for this entity.')

        return self._record_map[uid]

    def delete_record(self, entity):
        uid = self._retrieve_entity_guid(entity)

        if uid not in self._record_map:
            raise UOWUnknownRecordError('Unable to retrieve the record for this entity.')

        del self._record_map[uid]

    def has_record(self, entity):
        return self._retrieve_entity_guid(entity) in self._record_map

    def _retrieve_entity_guid(self, entity):
        return hash(entity)
