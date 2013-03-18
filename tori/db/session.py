from pymongo import Connection
from tori.db.common import ProxyObject, ProxyFactory, ProxyCollection
from tori.db.repository import Repository
from tori.db.exception import IntegrityConstraintError
from tori.db.mapper import AssociationType
from tori.db.uow import UnitOfWork

class Session(object):
    def __init__(self, id, database, registered_types={}):
        self._id               = id
        self._uow              = UnitOfWork(self)
        self._database         = database
        self._collections      = {}
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
        return [self.collection(self._registered_types[key]) for key in self._registered_types]

    def collection(self, entity_class):
        """Retrieve the collection

        :param entity_class: the class of document/entity
        :type  entity_class: type

        :rtype: tori.db.repository.Repository
        """
        key = entity_class.__collection_name__

        if key not in self._registered_types:
            self._registered_types[key] = entity_class

        if key not in self._collections:
            self._collections[key] = Repository(self, self._database[key], self._registered_types[key])

        return self._collections[key]

    def delete(self, *entities):
        for entity in entities:
            self._uow.register_deleted(entity)

    def refresh(self, *entities):
        for entity in entities:
            self.refresh_one(entity)

    def refresh_one(self, entity):
        self._uow.refresh(entity)

    def persist(self, *entities):
        for entity in entities:
            self.persist_one(entity)

    def persist_one(self, entity):
        registering_action = self._uow.register_new \
            if self._uow.is_new(entity) \
            else self._uow.register_dirty

        registering_action(entity)

    def flush(self):
        self._uow.commit()

    def register(self, entity_class):
        key = hash(entity_class)

        if key in self._collections:
            return

        self._collections[key] = Repository(self.database, entity_class)

    def register_multiple(self, *entity_classes):
        for entity_class in entity_classes:
            self.register(entity_class)

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
                else:
                    raise IntegrityConstraintError('Unknown type of entity association')

                return # Done the application

            # In the direct mapping, the lazy loading is applied wherever applicable.
            if guide.association in [AssociationType.ONE_TO_ONE, AssociationType.MANY_TO_ONE]:
                entity.__setattr__(property_name, ProxyFactory.make(self, entity.__getattribute__(property_name), guide))
            elif guide.association == AssociationType.ONE_TO_MANY:
                proxy_list = [
                    ProxyFactory.make(self, object_id, guide)
                    for object_id in entity.__getattribute__(property_name)
                ]

                entity.__setattr__(property_name, proxy_list)
            elif guide.association == AssociationType.MANY_TO_MANY:
                entity.__setattr__(property_name, ProxyCollection(self, entity, guide))
            else:
                raise IntegrityConstraintError('Unknown type of entity association')
