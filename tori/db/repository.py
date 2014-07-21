# -*- coding: utf-8 -*-
"""
:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Status: Stable
"""
import inspect
from tori.db.common    import PseudoObjectId, ProxyObject
from tori.db.criteria  import Query, Order
from tori.db.exception import MissingObjectIdException, EntityAlreadyRecognized, EntityNotRecognized
from tori.db.mapper    import AssociationType, CascadingType
from tori.db.uow       import Record
from tori.db.metadata.helper import EntityMetadataHelper

class Repository(object):
    """
    Repository (Entity AbstractRepository) for Mongo DB

    :param session: the entity manager
    :type  session: tori.db.session.Session
    :param representing_class: the representing class
    :type  representing_class: type

    A repository may automatically attempt to create an index if :meth:`auto_index`
    define the auto-index flag. Please note that the auto-index feature is only
    invoked when it tries to use a criteria with sorting or filtering with a
    certain type of conditions.
    """

    def __init__(self, session, representing_class):
        self._class   = representing_class
        self._session = session

        self._has_cascading = None
        self._auto_index    = False

        # Retrieve the collection
        self._session.register_class(representing_class)

    @property
    def session(self):
        """ Session

            :rtype: tori.db.session.Session
        """
        return self._session

    @property
    def driver(self):
        return self._session.driver

    @property
    def name(self):
        """ Collection name

            :rtype: str
        """
        metadata = EntityMetadataHelper.extract(self._class)

        return metadata.collection_name

    @property
    def kind(self):
        return self._class

    def auto_index(self, auto_index):
        """ Enable the auto-index feature

            :param auto_index: the index flag
            :type  auto_index: bool
        """
        self._auto_index = auto_index

    def new(self, **attributes):
        """ Create a new document/entity

            :param attributes: attribute map
            :return: object

            .. note::

                This method deal with data mapping.

        """
        spec = inspect.getargspec(self._class.__init__) # constructor contract
        meta = EntityMetadataHelper.extract(self._class)
        rmap = meta.relational_map # relational map

        # Default missing argument to NULL or LIST
        # todo: respect the default value of the argument
        for argument_name in spec.args:
            if argument_name == 'self' or argument_name in attributes:
                continue

            default_to_list = argument_name in rmap\
                and rmap[argument_name].association in [
                    AssociationType.ONE_TO_MANY,
                    AssociationType.MANY_TO_MANY
                ]

            attributes[argument_name] = [] if default_to_list else None

        attribute_name_list = list(attributes.keys())

        # Remove unwanted arguments/attributes/properties
        for attribute_name in attribute_name_list:
            if argument_name == 'self' or attribute_name in spec.args:
                continue

            del attributes[attribute_name]

        return self._class(**attributes)

    def get(self, id):
        data = self._session.driver.find_one(self.name, {'_id': id})

        if not data:
            return None

        return self._dehydrate_object(data)

    def find(self, criteria, force_loading=False):
        """ Find entity with criteria

            :param criteria: the search criteria
            :type  criteria: tori.db.criteria.Query
            :param force_loading: the flag to force loading all references behind the proxy
            :type  force_loading: bool

            :returns: the result based on the given criteria
            :rtype: object or list of objects
        """
        data_set = self.session.query(criteria)

        entity_list = []

        for data in data_set:
            entity = self._dehydrate_object(data) \
                if len(data.keys()) > 1 \
                else ProxyObject(
                    self._session,
                    self._class,
                    data['_id'],
                    False,
                    None,
                    False
                )
            record = self._session.find_record(id, self._class)

            if record and record.status in [Record.STATUS_DELETED, Record.STATUS_IGNORED]:
                continue

            entity_list.append(entity)

        if criteria._limit == 1:
            return entity_list[0] if entity_list else None

        return entity_list

    def count(self, criteria):
        """ Count the number of entities satisfied the given criteria

            :param criteria: the search criteria
            :type  criteria: tori.db.criteria.Query

            :rtype: int
        """
        return criteria.build_cursor(self).count()

    def filter(self, condition={}, force_loading=False):
        criteria = self.new_criteria()

        criteria._force_loading = force_loading

        criteria.where(condition)

        return self.find(criteria)

    def filter_one(self, condition={}, force_loading=False):
        criteria = self.new_criteria()

        criteria._force_loading = force_loading

        criteria.where(condition)
        criteria.limit(1)

        return self.find(criteria)

    def post(self, entity):
        if entity.__session__:
            raise EntityAlreadyRecognized('The entity has already been recognized by this session.')

        self._session.persist(entity)

        entity.__session__ = self._session

        self.commit()

        return entity.id

    def put(self, entity):
        self._recognize_entity(entity)
        self._session.persist(entity)
        self.commit()

    def delete(self, entity):
        self._recognize_entity(entity)
        self._session.delete(entity)
        self.commit()

    def persist(self, entity):
        self._session.persist(entity)

    def commit(self):
        self._session.flush()

    def _recognize_entity(self, entity):
        if not entity or not entity.id or not entity.__session__ or isinstance(entity.id, PseudoObjectId):
            raise EntityNotRecognized('The entity is not recognized by this session.')

    def _dehydrate_object(self, raw_data):
        if '_id' not in raw_data:
            raise MissingObjectIdException('The key _id in the raw data is not found.')

        id     = raw_data['_id']
        record = self._session.find_record(id, self._class)

        # Returned the known document from the record.
        if record:
            return record.entity

        data = dict(raw_data)

        del data['_id']

        document    = self.new(**data)
        document.id = id
        document.__session__ = self._session

        self._session.apply_relational_map(document)
        self._session.recognize(document)

        return document

    def has_cascading(self):
        if self._has_cascading is not None:
            return self._has_cascading

        self._has_cascading = False
        relational_map      = EntityMetadataHelper.extract(self._class).relational_map

        for property_name in relational_map:
            cascading_options = relational_map[property_name].cascading_options

            if cascading_options \
              and (
                  CascadingType.DELETE in cascading_options \
                  or CascadingType.PERSIST in cascading_options
              ):
                self._has_cascading = True

                break

        return self._has_cascading

    def new_criteria(self, alias='e'):
        """ Create a criteria

            :rtype: :class:`tori.db.criteria.Query`
        """

        c = Query(alias)

        c.origin = self._class

        if self._auto_index:
            c.auto_index(self._auto_index)

        return c

    def index(self, index, force_index=False):
        """ Index data

            :param index: the index
            :type  index: list, tori.db.entity.Index or str
            :param force_index: force indexing if necessary
            :type  force_index: bool
        """
        self._session.driver.ensure_index(self.name, index, force_index)

    def setup_index(self):
        """ Set up index for the entity based on the ``entity`` and ``link`` decorators
        """
        metadata = EntityMetadataHelper.extract(self._class)

        # Apply the relational indexes.
        for field in metadata.relational_map:
            guide = metadata.relational_map[field]

            if guide.inverted_by or guide.association != AssociationType.ONE_TO_ONE:
                continue

            self.index(field)

        # Apply the manual indexes.
        for index in metadata.index_list:
            self.index(index)

    def __len__(self):
        return self._session.driver.total_row_count(self.name)