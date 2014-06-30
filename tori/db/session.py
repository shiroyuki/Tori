
import re
from tori.db.common import ProxyObject, ProxyFactory, ProxyCollection
from tori.db.criteria import Criteria
from tori.db.repository import Repository
from tori.db.entity import get_relational_map
from tori.db.exception import IntegrityConstraintError
from tori.db.mapper import AssociationType
from tori.db.uow import UnitOfWork
from tori.db.metadata.helper import EntityMetadataHelper

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

    def repository(self, entity_class):
        """ Retrieve the collection

            :param entity_class: an entity class
            :type  entity_class: type

            :rtype: tori.db.repository.Repository
        """
        metadata = EntityMetadataHelper.extract(entity_class)
        key = metadata.collection_name

        self.register_class(entity_class)

        if key not in self._repository_map:
            repository = Repository(
                session=self,
                representing_class=entity_class
            )

            repository.setup_index()

            self._repository_map[key] = repository

        return self._repository_map[key]

    def register_class(self, entity_class):
        """ Register the entity class

            :param entity_class: the class of document/entity
            :type  entity_class: type

            :rtype: tori.db.repository.Repository
        """
        key = entity_class

        if isinstance(entity_class, type):
            metadata = EntityMetadataHelper.extract(entity_class)
            key      = metadata.collection_name

        if key not in self._registered_types:
            self._registered_types[key] = entity_class

    def query(self, query):
        if not query.is_new_style:
            return self.driver.query(query)

        collection_name = query.origin
        root_repo  = self.repository(collection_name)
        root_class = root_repo.kind
        expression_set = query.criteria.get_analyzed_version()

        # Fulfil the property-path-to-type map
        property_map = expression_set.properties # The property-path-to-type map

        # Register the root entity
        query.join_map[query.alias] = {
            'path': None,
            'class': root_class
        }

        self._update_join_map(query.join_map, query.alias, query.origin)

        metadata_origin = EntityMetadataHelper.extract(query.origin)

        result_list = self.driver.query(query)

        raise RuntimeError('Panda!')

        return result_list

    def _update_join_map(self, join_map, origin_alias, origin_class):
        origin_metadata = EntityMetadataHelper.extract(origin_class)
        link_map = origin_metadata.relational_map
        iterating_sequence = []

        #print('Updating {} ({})'.format(origin_alias, origin_class))

        for alias in join_map:
            join_config = join_map[alias]

            if join_config['class']:
                continue

            parent_alias, property_path = join_config['path'].split('.', 2)

            iterating_sequence.append((join_config, alias, parent_alias, property_path))

        # Update the immediate properties.
        for join_config, current_alias, parent_alias, property_path in iterating_sequence:
            #print('Immediate iterating: {} -> {}.{}'.format(current_alias, parent_alias, property_path))

            if parent_alias != origin_alias:
                #print('  - Skipped due to parent_alias')
                continue

            if property_path not in link_map:
                #print('  - Skipped as it is not mapped.')
                continue

            mapper = link_map[property_path]

            join_config['class']  = mapper.target_class
            join_config['mapper'] = mapper

            #print('  - Updated')

        # Update the joined properties.
        for join_config, current_alias, parent_alias, property_path in iterating_sequence:
            #print('Joined iterating: {} -> {}.{}'.format(current_alias, parent_alias, property_path))

            if current_alias not in join_map:
                #print('  - Skipped as {} not joined.'.format(current_alias))
                continue

            if not join_map[current_alias]['class']:
                #print('  - Skipped as class not defined')
                continue

            self._update_join_map(join_map, current_alias, join_map[current_alias]['class'])

            #print('  - Updated {}'.format(current_alias))

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