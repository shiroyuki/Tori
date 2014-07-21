
import re
from tori.db.common import ProxyObject, ProxyFactory, ProxyCollection
from tori.db.criteria import Criteria
from tori.db.repository import Repository
from tori.db.entity import get_relational_map
from tori.db.exception import IntegrityConstraintError, UnsupportedRepositoryReferenceError
from tori.db.mapper import AssociationType
from tori.db.metadata.entity import EntityMetadata
from tori.db.metadata.helper import EntityMetadataHelper
from tori.db.uow import UnitOfWork
from tori.graph import DependencyNode, DependencyManager

class QueryIteration(DependencyNode):
    def __init__(self, join_config, alias, parent_alias, property_path):
        super(QueryIteration, self).__init__()
        self._join_config   = join_config
        self._alias         = alias
        self._parent_alias  = parent_alias
        self._property_path = property_path

    @property
    def join_config(self):
        return self._join_config

    @property
    def alias(self):
        return self._alias

    @property
    def parent_alias(self):
        return self._parent_alias

    @property
    def property_path(self):
        return self._property_path

    def to_dict(self):
        return {
            'property_path': self.property_path,
            'parent_alias':  self.parent_alias,
            'alias':         self.alias,
            'join_config':   self.join_config,
            'adjacent_nodes':self.adjacent_nodes
        }

    def __repr__(self):
        return str('{}({})'.format(self.__class__.__name__, self.to_dict()))

class Session(object):
    """ Database Session

        :param database_name: the database name
        :param driver: the driver API
    """
    def __init__(self, driver):
        self._driver = driver
        self._uow    = UnitOfWork(self)
        self._repository_map   = {}
        self._registered_types = {}
        self._re_property_path_delimiter = re.compile('\.')

    @property
    def driver(self):
        return self._driver

    def collection(self, entity_class):
        """ Alias to ``repository()``

            .. deprecated:: 2.2
        """
        return self.repository(entity_class)

    def repositories(self):
        """ Retrieve the list of collections

            :rtype: list
        """
        return [self._repository_map[key] for key in self._repository_map]

    def repository(self, reference):
        """ Retrieve the collection

            :param reference: the entity class or entity metadata of the target repository / collection
            :rtype: tori.db.repository.Repository
        """
        key = None

        if isinstance(reference, EntityMetadata):
            key = reference.collection_name
        elif EntityMetadataHelper.hasMetadata(reference):
            is_registerable_reference = True

            metadata = EntityMetadataHelper.extract(reference)
            key      = metadata.collection_name

            self.register_class(reference)

        if not key:
            raise UnsupportedRepositoryReferenceError('Either a class with metadata or an entity metadata is supported.')

        if key not in self._repository_map:
            repository = Repository(
                session            = self,
                representing_class = reference
            )

            repository.setup_index()

            self._repository_map[key] = repository

        return self._repository_map[key]

    def register_class(self, entity_class):
        """ Register the entity class

            :param entity_class: the class of document/entity
            :type  entity_class: type

            :rtype: tori.db.repository.Repository

            .. note::

                This is for internal operation only. As it seems to be just a
                residual from the prototype stage, the follow-up investigation
                in order to remove the method will be for Tori 3.1.

        """
        key = entity_class

        if isinstance(entity_class, type):
            metadata = EntityMetadataHelper.extract(entity_class)
            key      = metadata.collection_name

        if key not in self._registered_types:
            self._registered_types[key] = entity_class

    def query(self, query):
        metadata = EntityMetadataHelper.extract(query.origin)

        # Deprecated in Tori 3.1; Only for backward compatibility
        if not query.is_new_style:
            return self.driver.query(
                metadata,
                query._condition,
                self.driver.dialect.get_iterating_constrains(query)
            )

        root_class     = query.origin
        expression_set = query.criteria.get_analyzed_version()

        # Register the root entity
        query.join_map[query.alias] = {
            'alias': query.alias,
            'path':  None,
            'class': root_class,
            'parent_alias': None,
            'property_path': None,
            'result_list': []
        }

        self._update_join_map(metadata, query.join_map, query.alias)

        iterating_sequence = self._compute_iterating_sequence(query.join_map)
        alias_to_query_map = self.driver.dialect.get_alias_to_native_query_map(query)

        for alias in query.join_map:
            mapping = query.join_map[alias]

        for iteration in iterating_sequence:
            if not self._sub_query(query, alias_to_query_map, iteration):
                break

        return query.join_map[query.alias]['result_list']

    def _sub_query(self, query, alias_to_query_map, iteration):
        is_join_query = True
        alias         = iteration.alias

        if alias not in alias_to_query_map:
            return False

        join_config  = query.join_map[alias]
        joined_type  = join_config['class']
        joined_meta  = EntityMetadataHelper.extract(joined_type)
        native_query = alias_to_query_map[alias]
        local_constrains = {}

        if not iteration.parent_alias:
            is_root    = False
            constrains = self.driver.dialect.get_iterating_constrains(query)

        result_list = self.driver.query(joined_meta, native_query, local_constrains)

        # No result in a sub-query means no result in the main query.
        if not result_list:
            return False

        join_config['result_list'] = result_list

        alias_to_query_map.update(self.driver.dialect.get_alias_to_native_query_map(query))

        return True

    def _compute_iterating_sequence(self, join_map):
        iterating_sequence = []
        joining_sequence   = []
        reference_map      = {}

        # reference_map is used locally for fast reverse lookup
        # iterating_seq is a final sequence

        # Calculate the iterating sequence
        for alias in join_map:
            join_config = join_map[alias]

            parent_alias  = None
            property_path = None

            if join_config['path']:
                parent_alias, property_path = join_config['path'].split('.', 2)

            qi = QueryIteration(join_config, alias, parent_alias, property_path)

            joining_sequence.append(qi)

            reference_map[alias] = qi

        # Update the dependency map
        for key in reference_map:
            reference_a = reference_map[key]

            if reference_a.parent_alias not in reference_map:
                continue

            reference_a.connect(reference_map[reference_a.parent_alias])

        iterating_sequence = DependencyManager.get_order(reference_map)
        iterating_sequence.reverse()

        return iterating_sequence

    def _update_join_map(self, origin_metadata, join_map, origin_alias):
        link_map           = origin_metadata.relational_map
        iterating_sequence = []

        # Compute the (local) iterating sequence for updating the join map.
        # Note: this is not the query iterating sequence.
        for alias in join_map:
            join_config = join_map[alias]

            if join_config['class']:
                continue

            parent_alias, property_path = join_config['path'].split('.', 2)

            join_config['alias']         = alias
            join_config['property_path'] = property_path
            join_config['parent_alias']  = parent_alias
            join_config['result_list']   = []

            iterating_sequence.append((join_config, alias, parent_alias, property_path))

        # Update the immediate properties.
        for join_config, current_alias, parent_alias, property_path in iterating_sequence:
            if parent_alias != origin_alias:
                continue

            if property_path not in link_map:
                continue

            mapper = link_map[property_path]

            join_config['class']  = mapper.target_class
            join_config['mapper'] = mapper

        # Update the joined properties.
        for join_config, current_alias, parent_alias, property_path in iterating_sequence:

            if current_alias not in join_map:
                continue

            if not join_map[current_alias]['class']:
                continue

            next_origin_class = join_map[current_alias]['class']
            next_metadata     = EntityMetadataHelper.extract(next_origin_class)
            self._update_join_map(next_metadata, join_map, current_alias)

    def delete(self, *entities):
        """ Delete entities

            :param entities: one or more entities
            :type  entities: type of list of type
        """
        for entity in entities:
            targeted_entity = self._force_load(entity)

            self._uow.register_deleted(targeted_entity)

    def refresh(self, *entities):
        """ Refresh entities

            :param entities: one or more entities
            :type  entities: type of list of type
        """
        for entity in entities:
            self.refresh_one(entity)

    def refresh_one(self, entity):
        self._uow.refresh(self._force_load(entity))

    def persist(self, *entities):
        """ Persist entities

            :param entities: one or more entities
            :type  entities: type of list of type
        """
        for entity in entities:
            self.persist_one(entity)

    def persist_one(self, entity):
        targeted_entity    = self._force_load(entity)
        registering_action = self._uow.register_new \
            if self._uow.is_new(targeted_entity) \
            else self._uow.register_dirty

        registering_action(targeted_entity)

    def recognize(self, entity):
        self._uow.register_clean(self._force_load(entity))

    def flush(self):
        """ Flush all changes of the session.
        """
        self._uow.commit()

    def find_record(self, id, cls):
        return self._uow.find_recorded_entity(id, cls)

    def apply_relational_map(self, entity):
        """ Wire connections according to the relational map """
        meta = EntityMetadataHelper.extract(entity)
        rmap = meta.relational_map

        for property_name in rmap:
            guide = rmap[property_name]
            """ :type: tori.db.mapper.RelatingGuide """

            # In the reverse mapping, the lazy loading is not possible but so
            # the proxy object is still used.
            if guide.inverted_by:
                target_meta = EntityMetadataHelper.extract(guide.target_class)

                api = self._driver.collection(target_meta.collection_name)

                if guide.association in [AssociationType.ONE_TO_ONE, AssociationType.MANY_TO_ONE]:
                    # Replace with Criteria
                    target = api.find_one({guide.inverted_by: entity.id})

                    entity.__setattr__(property_name, ProxyFactory.make(self, target['_id'], guide))
                elif guide.association == AssociationType.ONE_TO_MANY:
                    # Replace with Criteria
                    proxy_list = [
                        ProxyFactory.make(self, target['_id'], guide)
                        for target in api.find({guide.inverted_by: entity.id})
                    ]

                    entity.__setattr__(property_name, proxy_list)
                elif guide.association == AssociationType.MANY_TO_MANY:
                    entity.__setattr__(property_name, ProxyCollection(self, entity, guide))
                else:
                    raise IntegrityConstraintError('Unknown type of entity association (reverse mapping)')

                return # Done the application

            # In the direct mapping, the lazy loading is applied wherever applicable.
            if guide.association in [AssociationType.ONE_TO_ONE, AssociationType.MANY_TO_ONE]:
                if not entity.__getattribute__(property_name):
                    continue

                entity.__setattr__(
                    property_name,
                    ProxyFactory.make(
                        self,
                        entity.__getattribute__(property_name),
                        guide
                    )
                )
            elif guide.association == AssociationType.ONE_TO_MANY:
                proxy_list = []

                for object_id in entity.__getattribute__(property_name):
                    if not object_id:
                        continue

                    proxy_list.append(ProxyFactory.make(self, object_id, guide))

                entity.__setattr__(property_name, proxy_list)
            elif guide.association == AssociationType.MANY_TO_MANY:
                entity.__setattr__(property_name, ProxyCollection(self, entity, guide))
            else:
                raise IntegrityConstraintError('Unknown type of entity association')

    def _force_load(self, entity):
        return entity._actual \
            if isinstance(entity, ProxyObject) \
            else entity