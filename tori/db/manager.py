from pymongo import Connection
from tori.db.common import ProxyObject
from tori.db.collection import Collection
from tori.db.exception import IntegrityConstraintError
from tori.db.mapper import AssociationType
from tori.db.uow import UnitOfWork

class Manager(object):
    def __init__(self, name, connection=None, document_types=[]):
        """Constructor

        :param name: the name of the database
        :type  name: str
        :param connection: the database connection
        :type  connection: pymongo.Connection
        """
        self._uow  = UnitOfWork(self)
        self._name = name
        self._connection  = connection or Connection()
        self._database    = self._connection[self._name]
        self._collections = {}
        self._registered_types = {}

        for document_type in document_types:
            self._registered_types[document_type.__collection_name__] = document_type

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

        :rtype: tori.db.collection.Collection
        """
        key = entity_class.__collection_name__

        if key not in self._registered_types:
            return None

        if key not in self._collections:
            self._collections[key] = Collection(self, self._database[key], self._registered_types[key])

        return self._collections[key]

    def delete(self, *entities):
        for entity in entities:
            self._uow.register_deleted(entity)

    def persist(self, *entities):
        for entity in entities:
            self.persist_one(entity)

    def refresh(self, *entities):
        for entity in entities:
            self.refresh_one(entity)

    def refresh_one(self, entity):
        self._uow.refresh(entity)

    def persist_one(self, entity):
        registering_action = self._uow.register_new\
            if self._uow.is_new(entity)\
            else self._uow.register_dirty

        registering_action(entity)

    def flush(self):
        self._uow.commit()

    def register(self, entity_class):
        key = hash(entity_class)

        if key in self._collections:
            return

        self._collections[key] = Collection(self.database, entity_class)

    def register_multiple(self, *entity_classes):
        for entity_class in entity_classes:
            self.register(entity_class)

    def apply_relational_map(self, entity):
        for property_name in entity.__relational_map__:
            guide = entity.__relational_map__[property_name]
            """ :type: tori.db.mapper.RelatingGuide """

            if guide.association in [AssociationType.ONE_TO_ONE, AssociationType.MANY_TO_ONE]:
                proxy = ProxyObject(
                    self,
                    guide.target_class,
                    entity.__getattribute__(property_name),
                    guide.read_only,
                    guide.cascading_options
                )

                entity.__setattr__(property_name, proxy)
            elif guide.association == AssociationType.ONE_TO_MANY:
                proxy_list = []

                for object_id in entity.__getattribute__(property_name):
                    proxy_list.append(
                        ProxyObject(
                            self,
                            guide.target_class,
                            object_id,
                            guide.read_only,
                            guide.cascading_options
                        )
                    )

                entity.__setattr__(property_name, proxy_list)
            elif guide.association == AssociationType.MANY_TO_MANY:
                proxy_list   = []
                map_name     = guide.association_collection_name(entity)
                mapping_list = self.db[map_name].find({'from': entity.id})

                for data_set in mapping_list:
                    object_id = data_set['to']

                    proxy_list.append(
                        ProxyObject(
                            self,
                            guide.target_class,
                            object_id,
                            guide.read_only,
                            guide.cascading_options
                        )
                    )

                entity.__setattr__(property_name, proxy_list)
            else:
                raise IntegrityConstraintError('Unknown type of entity association')

    def _get_class_key(self, entity):
        return hash(entity.__class__)
