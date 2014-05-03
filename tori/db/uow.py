# -*- coding: utf-8 -*-
from time      import time
from threading import Lock as ThreadLock
from tori.graph import DependencyNode as BaseDependencyNode, DependencyManager
from tori.db.common    import Serializer, PseudoObjectId, ProxyObject
from tori.db.entity    import BasicAssociation
from tori.db.exception import UOWRepeatedRegistrationError, UOWUpdateError, UOWUnknownRecordError, IntegrityConstraintError
from tori.db.mapper    import CascadingType
from tori.db.metadata.helper import EntityMetadataHelper

class Record(object):
    serializer = Serializer(0)

    STATUS_CLEAN     = 1
    STATUS_DELETED   = 2
    STATUS_DIRTY     = 3
    STATUS_NEW       = 4
    STATUS_IGNORED   = 5

    STATUS_LABEL_MAP = {
        1: 'clean',
        2: 'deleted',
        3: 'dirty',
        4: 'new',
        5: 'ignored'
    }

    def __init__(self, entity, status):
        self.entity  = entity
        self.status  = status
        self.updated = time()

        self.original_data_set          = Record.serializer.encode(self.entity)
        self.original_extra_association = Record.serializer.extra_associations(self.entity)

    def mark_as(self, status):
        self.status  = status
        self.updated = time()

    def update(self):
        self.original_data_set          = Record.serializer.encode(self.entity)
        self.original_extra_association = Record.serializer.extra_associations(self.entity)

        self.mark_as(Record.STATUS_CLEAN)

class DependencyNode(BaseDependencyNode):
    """ Dependency Node

        This is designed to be bi-directional to maximize flexibility on
        traversing the graph.
    """
    def __init__(self, record):
        super(DependencyNode, self).__init__()

        self.record = record

    @property
    def object_id(self):
        return self.record.entity.id

    @property
    def status(self):
        return self.record.status

    def _disavow_connection(self, node):
        return node.status == Record.STATUS_DELETED

    def __eq__(self, other):
        return self.record.entity.__class__ == other.record.entity.__class__ and self.object_id == other.object_id

    def __ne__(self, other):
        return self.record.entity.__class__ != other.record.entity.__class__ or self.object_id != other.object_id

    def __hash__(self):
        return self.created_at

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
        self._blocking_lock     = ThreadLock()
        self._operational_lock  = ThreadLock()

    def _freeze(self):
        if not self._blocker_activated:
            return

        self._operational_lock.acquire()

    def _unfreeze(self):
        if not self._blocker_activated:
            return

        self._operational_lock.release()

    def refresh(self, entity):
        """ Refresh the entity

            .. note:: This method

            :param entity: the target entity
            :type  entity: object
        """
        self._freeze()

        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_DELETED:
            return # Ignore the entity marked as deleted.
        elif record.status not in [Record.STATUS_CLEAN, Record.STATUS_DIRTY]:
            raise NonRefreshableEntity('The current record is not refreshable.')

        collection       = self._em.collection(entity.__class__)
        updated_data_set = collection.driver.find_one(collection.name, {'_id': entity.id})

        # Reset the attributes.
        for attribute_name in updated_data_set:
            entity.__setattr__(attribute_name, updated_data_set[attribute_name])

        # Remove the non-existed attributes.
        for attribute_name in record.original_data_set:
            if attribute_name in updated_data_set:
                continue

            entity.__delattr__(attribute_name)

        # Update the original data set and reset the status if necessary.
        record.original_data_set = Record.serializer.encode(entity)
        record.extra_association = Record.serializer.extra_associations(entity)

        if record.status == Record.STATUS_DIRTY:
            record.mark_as(Record.STATUS_CLEAN)

        # Remap any one-to-many or many-to-many relationships.
        self._em.apply_relational_map(entity)

        self._cascade_operation(entity, CascadingType.REFRESH)

        self._unfreeze()

    def register_new(self, entity):
        """ Register a new entity

            :param entity: the entity to register
            :type  entity: object
        """
        self._freeze()

        self._register_new(entity)

        self._unfreeze()

    def _register_new(self, entity):
        """ Register a entity as new (protected)

            .. warning::

                This method bypasses the thread lock imposed in the public
                method. It is for internal use only.

            :param entity: the target entity
            :type  entity: object
        """
        uid = self._retrieve_entity_guid(entity)

        if self.has_record(entity):
            raise UOWRepeatedRegistrationError('Could not mark the entity as new.')

        if not entity.id:
            entity.id = self._generate_pseudo_object_id()

        self._record_map[uid] = Record(entity, Record.STATUS_NEW)

        # Map the pseudo object ID to the entity.
        self._object_id_map[self._convert_object_id_to_str(entity.id, entity)] = uid

        self._cascade_operation(entity, CascadingType.PERSIST)

    def register_dirty(self, entity):
        """ Register the entity with the dirty bit

            :param entity: the entity to register
            :type  entity: object
        """

        self._freeze()

        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_NEW:
            try:
                return self.register_new(entity)
            except UOWRepeatedRegistrationError as exception:
                pass
        elif record.status in [Record.STATUS_CLEAN, Record.STATUS_DELETED]:
            record.mark_as(Record.STATUS_DIRTY)

        self._cascade_operation(entity, CascadingType.PERSIST)

        self._unfreeze()

    def register_clean(self, entity):
        """ Register the entity with the clean bit

            :param entity: the entity to register
            :type  entity: object
        """

        uid = self._retrieve_entity_guid(entity)

        if uid in self._record_map:
            raise UOWRepeatedRegistrationError('Could not mark the entity as clean')

        self._record_map[uid] = Record(entity, Record.STATUS_CLEAN)

        # Map the real object ID to the entity
        self._object_id_map[self._convert_object_id_to_str(entity.id, entity)] = uid

    def register_deleted(self, entity):
        """ Register the entity with the removal bit

            :param entity: the entity to register
            :type  entity: object
        """

        self._freeze()

        self._register_deleted(entity)

        self._unfreeze()

    def _register_deleted(self, entity):
        """ Register a entity as deleted (no lock)

            .. warning:: This method bypasses the thread lock imposed in the public method. It is for internal use only.

            :param entity: the target entity
            :type  entity: object
        """
        record = self.retrieve_record(entity)

        if record.status == Record.STATUS_NEW or isinstance(entity.id, PseudoObjectId):
            record.mark_as(Record.STATUS_IGNORED)
        else:
            record.mark_as(Record.STATUS_DELETED)

        self._cascade_operation(entity, CascadingType.DELETE)

    def _cascade_operation(self, reference, cascading_type):
        entity = reference

        if isinstance(reference, ProxyObject):
            entity = reference._actual

        if not EntityMetadataHelper.hasMetadata(entity):
            return

        entity_meta = EntityMetadataHelper.extract(entity)
        relational_map = entity_meta.relational_map

        for property_name in relational_map:
            guide = relational_map[property_name]

            if guide.inverted_by:
                continue

            actual_data = entity.__getattribute__(property_name)
            reference   = self.hydrate_entity(actual_data)

            if not guide.cascading_options\
                or cascading_type not in guide.cascading_options\
                or not reference:
                continue

            if isinstance(reference, list):
                for sub_reference in actual_data:
                    self._forward_operation(
                        self.hydrate_entity(sub_reference),
                        cascading_type,
                        guide.target_class
                    )

                continue

            self._forward_operation(
                reference,
                cascading_type,
                guide.target_class
            )

    def _forward_operation(self, reference, cascading_type, expected_class):
        if cascading_type == CascadingType.PERSIST:
            if type(reference) is not expected_class:
                reference_type = type(reference)

                raise IntegrityConstraintError(
                    'Expected an instance of class {} ({}) but received one of {} ({})'.format(
                        expected_class.__name__,
                        expected_class.__module__,
                        reference_type.__name__,
                        reference_type.__module__
                    )
                )

            if self.is_new(reference):
                try:
                    self.register_new(reference)
                except UOWRepeatedRegistrationError as exception:
                    pass
            else:
                self.register_dirty(reference)
        elif cascading_type == CascadingType.DELETE:
            self.register_deleted(reference)
        elif cascading_type == CascadingType.REFRESH:
            self.refresh(reference)

    def is_new(self, reference):
        return not reference.id or isinstance(reference.id, PseudoObjectId)

    def hydrate_entity(self, reference):
        return reference._actual if isinstance(reference, ProxyObject) else reference

    def commit(self):
        self._blocking_lock.acquire()

        self._blocker_activated = True

        self._freeze()

        # Make changes on the normal entities.
        self._commit_changes()

        # Then, make changes on external associations.
        self._add_or_remove_associations()
        self._commit_changes(BasicAssociation)

        # Synchronize all records
        self._synchronize_records()

        self._unfreeze()

        self._blocker_activated = False

        self._blocking_lock.release()

    def _commit_changes(self, expected_class=None):
        # Load the sub graph of supervised collections.
        for c in self._em.repositories():
            if not c.has_cascading():
                continue

            c.filter(force_loading=True)

        commit_order = self._compute_order()

        # Commit changes to nodes.
        for commit_node in commit_order:
            uid    = self._retrieve_entity_guid_by_id(commit_node.object_id, commit_node.record.entity.__class__)
            record = self._record_map[uid]

            if expected_class and not isinstance(record.entity, expected_class):
                continue

            collection = self._em.collection(record.entity.__class__)
            change_set = self._compute_change_set(record)

            if record.status == Record.STATUS_NEW:
                self._synchronize_new(
                    collection,
                    record.entity,
                    change_set
                )
            elif record.status == Record.STATUS_DIRTY and change_set:
                self._synchronize_update(
                    collection,
                    record.entity.id,
                    record.original_data_set,
                    change_set
                )
            elif record.status == Record.STATUS_DIRTY and not change_set:
                record.mark_as(Record.STATUS_CLEAN)
            elif record.status == Record.STATUS_DELETED and commit_node.score == 0:
                self._synchronize_delete(collection, record.entity.id)
            elif record.status == Record.STATUS_DELETED and commit_node.score > 0:
                record.mark_as(Record.STATUS_CLEAN)

    def _synchronize_new(self, repository, entity, change_set):
        """ Synchronize the new / unsupervised data

            :param repository: the target repository
            :param entity: the entity
            :param change_set: the change_set representing the entity
        """
        pseudo_key = self._convert_object_id_to_str(entity.id, entity)
        object_id  = repository.driver.insert(repository.name, change_set)
        entity.id  = object_id # update the entity ID
        actual_key = self._convert_object_id_to_str(object_id, entity)

        self._object_id_map[actual_key] = self._object_id_map[pseudo_key]

    def _synchronize_update(self, repository, object_id, old_data_set, new_data_set):
        """ Synchronize the updated data

            :param repository: the target repository
            :param object_id: the object ID
            :param old_data_set: the original data (for event interception)
            :param new_data_set: the updated data
        """

        repository.driver.update(
            repository.name,
            {'_id': object_id},
            new_data_set
        )

    def _synchronize_delete(self, repository, object_id):
        """ Synchronize the deleted data

            :param repository: the target repository
            :param object_id: the object ID
        """
        repository.driver.remove(repository.name, {'_id': object_id})

    def _synchronize_records(self):
        writing_statuses = [Record.STATUS_NEW, Record.STATUS_DIRTY]
        removed_statuses = [Record.STATUS_DELETED, Record.STATUS_IGNORED]
        uid_list         = list(self._record_map.keys())

        for uid in uid_list:
            record = self._record_map[uid]

            if record.status in removed_statuses:
                del self._record_map[uid]
            elif record.status in writing_statuses:
                record.update()

    def retrieve_record(self, entity):
        uid = self._retrieve_entity_guid(self._em._force_load(entity))

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

    def find_recorded_entity(self, object_id, cls):
        object_key = self._convert_object_id_to_str(object_id, cls=cls)

        if object_key in self._object_id_map:
            try:
                return self._record_map[self._object_id_map[object_key]]
            except KeyError as exception:
                # This exception is raised possibly due to that the record is deleted.
                del self._object_id_map[object_key]

        return None

    def _compute_order(self):
        self._construct_dependency_graph()

        # After constructing the dependency graph (as a supposedly directed acyclic
        # graph), do the topological sorting from the dependency graph.
        return DependencyManager.get_order(self._dependency_map)

    def _compute_change_set(self, record):
        current_set = Record.serializer.encode(record.entity)

        if record.status == Record.STATUS_NEW:
            return current_set
        elif record.status == Record.STATUS_DELETED:
            return record.entity.id

        original_set = dict(record.original_data_set)

        change_set = {
            '$set':   {},
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

    def _compute_connection_changes(self, record):
        """ Compute changes in external associations originated from the entity
        of the current record

        This method is designed specifically to deal with many-to-many
        association by adding or removing associative entities which their
        origin is from the entity from the current record.

        :param record: the UOW record
        :type  record: tori.db.uow.Record
        """
        current  = Record.serializer.extra_associations(record.entity)
        original = dict(record.original_extra_association)

        change_set = {}

        original_property_set = set(original.keys())
        current_property_set  = set(current.keys())

        expected_property_list = original_property_set.intersection(current_property_set)
        expected_property_list = expected_property_list.union(current_property_set.difference(original_property_set))

        unexpected_property_list = expected_property_list if record.status == Record.STATUS_DELETED else original_property_set.difference(current_property_set)

        # Find new associations
        for name in expected_property_list:
            current_set  = set(current[name])
            original_set = set(original[name])

            diff_additions = current_set
            diff_deletions = []

            if record.status != Record.STATUS_NEW:
                diff_additions = current_set.difference(original_set)
                diff_deletions = original_set.difference(current_set)

            change_set[name] = {
                'action':  'update',
                'new':     diff_additions,
                'deleted': diff_deletions
            }

        # Find new associations
        for name in unexpected_property_list:
            change_set[name] = {
                'action': 'purge'
            }

        return change_set

    def _load_extra_associations(self, record, change_set):
        origin_id      = record.entity.id
        relational_map = EntityMetadataHelper.extract(record.entity).relational_map

        for property_name in relational_map:
            if property_name not in change_set:
                continue

            property_change_set = change_set[property_name]
            guide      = relational_map[property_name]
            repository = self._em.collection(guide.association_class.cls)

            if property_change_set['action'] == 'update':
                for unlinked_destination_id in property_change_set['deleted']:
                    association = repository.filter_one({'origin': origin_id, 'destination': unlinked_destination_id})

                    if not association:
                        continue

                    self._register_deleted(association)

                for new_destination_id in property_change_set['new']:
                    association = repository.new(origin=origin_id, destination=new_destination_id)

                    self._register_new(association)

                return
            elif property_change_set['action'] == 'purge':
                for association in repository.filter({'origin': origin_id}):
                    self._register_deleted(association)

                return

            raise RuntimeError('Unknown changes on external associations for {}'.format(origin_id))

    def _add_or_remove_associations(self):
        # Find out if UOW needs to deal with extra records (associative collection).
        uid_list = list(self._record_map.keys())

        for uid in uid_list:
            record = self._record_map[uid]

            if record.status == Record.STATUS_CLEAN:
                continue

            change_set = self._compute_connection_changes(record)

            if not change_set:
                continue

            self._load_extra_associations(record, change_set)

    def _retrieve_entity_guid(self, entity):
        return self._retrieve_entity_guid_by_id(entity.id, entity.__class__)\
            if isinstance(entity, ProxyObject)\
            else hash(entity)

    def _retrieve_entity_guid_by_id(self, id, cls):
        return self._object_id_map[self._convert_object_id_to_str(id, cls=cls)]

    def _generate_pseudo_object_id(self):
        return PseudoObjectId()

    def _convert_object_id_to_str(self, object_id, entity=None, cls=None):
        class_hash = 'generic'

        if not cls and entity:
            cls = entity.__class__

        if cls:
            metadata   = EntityMetadataHelper.extract(cls)
            class_hash = metadata.collection_name

        object_key = '{}/{}'.format(class_hash, str(object_id))

        return object_key

    def _construct_dependency_graph(self):
        self._dependency_map = {}

        for uid in self._record_map:
            record = self._record_map[uid]

            object_id = self._convert_object_id_to_str(record.entity.id, record.entity)

            current_set       = Record.serializer.encode(record.entity)
            extra_association = Record.serializer.extra_associations(record.entity)

            # Register the current entity into the dependency map if it's never
            # been registered or eventually has no dependencies.
            if object_id not in self._dependency_map:
                self._dependency_map[object_id] = DependencyNode(record)

            relational_map = EntityMetadataHelper.extract(record.entity).relational_map

            if not relational_map:
                continue

            # Go through the relational map to establish relationship between dependency nodes.
            for property_name in relational_map:
                guide = relational_map[property_name]

                # Ignore a property from reverse mapping.
                if guide.inverted_by:
                    continue

                # ``data`` can be either an object ID or list.
                data = current_set[property_name]

                if not data:
                    # Ignore anything evaluated as False.
                    continue
                elif not isinstance(data, list):
                    other_uid    = self._retrieve_entity_guid_by_id(data, guide.target_class)
                    other_record = self._record_map[other_uid]

                    self._register_dependency(record, other_record)

                    continue

                for dependency_object_id in data:
                    other_uid    = self._retrieve_entity_guid_by_id(dependency_object_id, guide.target_class)
                    other_record = self._record_map[other_uid]

                    self._register_dependency(record, other_record)

        return self._dependency_map

    def _retrieve_dependency_order(self, node, priority_order):
        if node.walked:
            return

        node.walked = True

        initial_order = list(node.adjacent_nodes)

        for adjacent_node in initial_order:
            self._retrieve_dependency_order(adjacent_node, priority_order)

        if node not in priority_order:
            priority_order.append(node)

    def _register_dependency(self, a, b):
        key_a = self._convert_object_id_to_str(a.entity.id, a.entity)
        key_b = self._convert_object_id_to_str(b.entity.id, b.entity)

        if key_a not in self._dependency_map:
            self._dependency_map[key_a] = DependencyNode(a)

        if key_b not in self._dependency_map:
            self._dependency_map[key_b] = DependencyNode(b)

        self._dependency_map[key_a].connect(self._dependency_map[key_b])
