from pymongo import Connection
from tori.db.common import ProxyObject, ProxyFactory, ProxyCollection
from tori.db.repository import Repository
from tori.db.exception import IntegrityConstraintError
from tori.db.mapper import AssociationType
from tori.db.uow import UnitOfWork

class Session(object):
    """ Database Session

        :param id: the unique identifier of the session
        :type  id: int or bson.objectid.ObjectId
        :param database: the database connection
        :type  database:
    """
    def __init__(self, id, database, registered_types={}):
        self._id  = id
        self._uow = UnitOfWork(self)
        self._database = database
        self._repository_map   = {}
        self._registered_types = registered_types

    @property
    def id(self):
        return self._id

    @property
    def db(self):
        """ Database-level API

        :rtype: pymongo.database.Database

        .. warning::

            Please use this property with caution. The unit of work cannot track any changes done by direct calls via
            this property and may mess up with the change-set calculation.

        """
        return self._database

    @property
    def collections(self):
        """ Alias to ``repositories`` """
        return self.repositories

    def collection(self, entity_class):
        """ Alias to ``repository()`` """
        return self.repository(entity_class)

    @property
    def repositories(self):
        """ Retrieve the list of used repositories.

            :rtype: list
        """
        return [
            self.collection(self._registered_types[key])
            for key in self._registered_types
        ]

    def repository(self, entity_class):
        """ Retrieve the collection

            :param entity_class: an entity class
            :type  entity_class: type

            :rtype: tori.db.repository.Repository
        """
        key = entity_class.__collection_name__

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
        """Register the entity class

        :param entity_class: the class of document/entity
        :type  entity_class: type

        :rtype: tori.db.repository.Repository
        """
        key = entity_class.__collection_name__

        if key not in self._registered_types:
            self._registered_types[key] = entity_class

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
        for property_name in entity.__relational_map__:
            guide = entity.__relational_map__[property_name]
            """ :type: tori.db.mapper.RelatingGuide """

            # In the reverse mapping, the lazy loading is not possible but so the proxy object is still used.
            if guide.inverted_by:
                collection = self.collection(guide.target_class)

                if guide.association in [AssociationType.ONE_TO_ONE, AssociationType.MANY_TO_ONE]:
                    target = collection._api.find_one({guide.inverted_by: entity.id})

                    entity.__setattr__(property_name, ProxyFactory.make(self, target['_id'], guide))
                elif guide.association == AssociationType.ONE_TO_MANY:
                    proxy_list = [
                        ProxyFactory.make(self, target['_id'], guide)
                        for target in collection._api.find({guide.inverted_by: entity.id})
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