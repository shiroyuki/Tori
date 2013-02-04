from time import time
from threading import Lock as ThreadLock
from tori.db.common    import Serializer, PseudoObjectId, ProxyObject, EntityCollection
from tori.db.exception import UOWRepeatedRegistrationError, UOWUpdateError, UOWUnknownRecordError
from tori.db.mapper import CascadingType

class Record(object):
    serializer = Serializer(0)

    STATUS_CLEAN     = 1
    STATUS_DELETED   = 2
    STATUS_DIRTY     = 3
    STATUS_NEW       = 4

    def __init__(self, entity, status):
        self.entity = entity
        self.status = status

        self.original_data_set = Record.serializer.encode(entity)

    def update(self):
        self.original_data_set = Record.serializer.encode(self.entity)
        self.status = Record.STATUS_CLEAN

class DependencyNode(object):
    def __init__(self, object_id):
        self.created_at     = int(time() * 1000000)
        self.object_id      = object_id
        self.adjacent_nodes = set()

    @property
    def score(self):
        return len(self.adjacent_nodes)

    def __eq__(self, other):
        return self.object_id == other.object_id

    def __ne__(self, other):
        return self.object_id != other.object_id

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __hash__(self):
        return self.created_at

    def __repr__(self):
        return '<DependencyNode for {}, {}>'.format(self.object_id, self.score)

class UnitOfWork(object):
    """ Unit of Work

    This Unit of Work (UOW) is designed specifically for non-relational databases.

    .. note::

        It is the design decision to make sub-commit methods available so that when it is used with Imagination
        Framework, the other Imagination entity may intercept before or after actually committing data. In the other
        word, Imagination Framework acts as an event controller for any actions (public methods) of this class.

    """
    serializer = Serializer(0)

    def __init__(self, entity_manager):
        # given property
        self._em = entity_manager

        # caching properties
        self._record_map    = {} # Object Hash => Record
        self._object_id_map = {} # str(ObjectID) => Object Hash
        self._dependency_map = None

        # Locks
        self._blocker_activated = False
        self._tlock = ThreadLock()

    def freeze(self):
        if not self._blocker_activated:
            return

        self._tlock.acquire()

    def unfreeze(self):
        if not self._blocker_activated:
            return

        self._tlock.release()

    def register_new(self, entity):
        self.freeze()

        uid = self._retrieve_entity_guid(entity)

        if self.has_record(entity):
            raise UOWRepeatedRegistrationError('Could not mark the entity as new.')

        if not entity.id:
            entity.id = self._generate_pseudo_object_id()

        self._record_map[uid] = Record(entity, Record.STATUS_NEW)

        # Map the pseudo object ID to the entity.
        self._object_id_map[self._convert_object_id_to_str(entity.id)] = uid

        self.cascade_property_registration_of(entity, CascadingType.PERSIST)

        self.unfreeze()

    def register_dirty(self, entity):
        self.freeze()

        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_DELETED:
            raise UOWUpdateError('Could not update the deleted entity.')

        if record.status == Record.STATUS_NEW or not self.compute_change_set(record):
            return

        record.status = Record.STATUS_DIRTY

        self.cascade_property_registration_of(entity, CascadingType.PERSIST)

        self.unfreeze()

    def register_clean(self, entity):
        self.freeze()

        uid = self._retrieve_entity_guid(entity)

        if uid in self._record_map:
            raise UOWRepeatedRegistrationError('Could not mark the entity as clean')

        self._record_map[uid] = Record(entity, Record.STATUS_CLEAN)

        # Map the real object ID to the entity
        self._object_id_map[self._convert_object_id_to_str(entity.id)] = uid

        self.unfreeze()

    def register_deleted(self, entity):
        self.freeze()

        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_NEW:
            self.delete_record(entity)

            return

        record.status = Record.STATUS_DELETED

        self.cascade_property_registration_of(entity, CascadingType.DELETE)

        self.unfreeze()

    def cascade_property_registration_of(self, entity, cascading_type):
        if '__relational_map__' not in dir(entity):
            return

        for property_name in entity.__relational_map__:
            guide     = entity.__relational_map__[property_name]
            reference = self.eager_load(entity.__getattribute__(property_name))

            if not guide.cascading_options\
              or cascading_type not in guide.cascading_options\
              or not reference:
                continue

            if isinstance(reference, EntityCollection):
                for sub_reference in reference:
                    self._register_by_cascading_type(
                        self.eager_load(sub_reference),
                        cascading_type
                    )

            self._register_by_cascading_type(reference, cascading_type)

    def _register_by_cascading_type(self, reference, cascading_type):
        if cascading_type == CascadingType.PERSIST:
            if self.is_new(reference):
                try:
                    self.register_new(reference)
                except UOWRepeatedRegistrationError as exception:
                    pass
            else:
                self.register_dirty(reference)
        elif cascading_type == CascadingType.DELETE:
            self.register_deleted(reference)

    def is_new(self, reference):
        return not reference.id or isinstance(reference.id, PseudoObjectId)

    def eager_load(self, reference):
        return reference._actual if isinstance(reference, ProxyObject) else reference

    def commit(self):
        self._blocker_activated = True

        self.freeze()

        commit_order = self.compute_order()

        for commit_node in commit_order:
            uid    = self._object_id_map[self._convert_object_id_to_str(commit_node.object_id)]
            record = self._record_map[uid]

            collection = self._em.collection(record.entity.__class__)
            change_set = self.compute_change_set(record)

            if record.status == Record.STATUS_NEW:
                self.synchronize_new(
                    collection,
                    record.entity,
                    change_set
                )
            elif record.status == Record.STATUS_DIRTY:
                self.synchronize_update(
                    collection,
                    record.entity.id,
                    record.original_data_set,
                    change_set
                )
            elif record.status == Record.STATUS_DELETED:
                self.synchronize_delete(collection, record.entity.id)

        self.synchronize_records()
        self.unfreeze()

        self._blocker_activated = False

    def synchronize_new(self, collection, entity, change_set):
        object_id = collection._api.insert(change_set)
        entity.id = object_id # update the entity ID

        self._record_map[entity.id] = entity

    def synchronize_update(self, collection, object_id, old_data_set, new_data_set):
        """Synchronize the updated data

        :param collection: the target collection
        :param object_id: the object ID
        :param old_data_set: the original data (for event interception)
        :param new_data_set: the updated data
        """
        collection._api.update(
            {'_id': object_id},
            new_data_set,
            upsert=False
        )

    def synchronize_delete(self, collection, object_id):
        collection._api.remove({'_id': object_id})

    def synchronize_records(self):
        self._record_map    = {}
        self._object_id_map = {}

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

    def find_recorded_entity(self, object_id):
        key = self._convert_object_id_to_str(object_id)

        if key in self._object_id_map:
            return self._object_id_map[key]

        return None

    def _retrieve_entity_guid(self, entity):
        return hash(entity)

    def _generate_pseudo_object_id(self):
        return PseudoObjectId()

    def _convert_object_id_to_str(self, object_id):
        key = str(object_id)

        if isinstance(object_id, PseudoObjectId):
            key = 'pseudo/{}'.format(key)

        return key

    def compute_order(self):
        self._dependency_map = {}

        for uid in self._record_map:
            record = self._record_map[uid]

            if not record.entity.__relational_map__:
                continue

            object_id   = record.entity.id
            current_set = Record.serializer.encode(record.entity)

            for property_name in record.entity.__relational_map__:
                data = current_set[property_name]

                if not data:
                    continue
                elif not isinstance(data, list):
                    self._register_dependency(object_id, data)

                    continue

                for dependency_object_id in data:
                    self._register_dependency(object_id, dependency_object_id)

        # After constructing the dependency graph (as a supposedly directed acyclic graph), do topological sorting.
        final_order = []

        for id in self._dependency_map:
            node = self._dependency_map[id]

            self._retrieve_dependency_order(node, final_order)

        return final_order

    def _retrieve_dependency_order(self, node, priority_order):
        initial_order = list(node.adjacent_nodes)

        for adjacent_node in initial_order:
            self._retrieve_dependency_order(adjacent_node, priority_order)

        if node not in priority_order:
            priority_order.append(node)

    def _register_dependency(self, a, b):
        if a not in self._dependency_map:
            self._dependency_map[a] = DependencyNode(a)

        if b not in self._dependency_map:
            self._dependency_map[b] = DependencyNode(b)

        self._dependency_map[a].adjacent_nodes.add(self._dependency_map[b])

    def compute_change_set(self, record):
        current_set = Record.serializer.encode(record.entity)

        if record.status == Record.STATUS_NEW:
            return current_set
        elif record.status == Record.STATUS_DELETED:
            return record.entity.id

        original_set = dict(record.original_data_set)

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