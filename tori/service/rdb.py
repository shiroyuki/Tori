'''
:Author: Juti Noppornpitak

The default relational database service for Tori framework.
'''

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from tori.exception import *
from tori.rdb       import Entity as BaseEntity

class RelationalDatabaseService(object):
    '''
    This service provides basic functionality to interact a relational database.

    It also heavily uses lazy loading for the sake of faster startup and resource efficiency.

    :param `url`: a URL to the database, possibly including location, credential and name.\
                  The default value is ``sqlite:///:memory:``.
    '''
    def __init__(self, url='sqlite:///:memory:'):
        self._engine    = None
        self._url       = url
        self._reflected = False
        self._session   = None
        self._session_class   = None
        self._primary_session = None

    def engine(self):
        '''
        Get the SQLAlchemy engine.

        .. note::
            With the service, it is not recommended to directly use this method.
        '''
        if not self._engine:
            self._configure_engine()

        return self._engine

    def _configure_engine(self):
        self._engine = create_engine(
            self._url,
            echo=False
        )

    def url(self, new_url=None):
        '''
        Get the connecting URL.

        :param `new_url`: a new URL for the database connection.
        '''
        if not new_url:
            self._url = new_url

            self._configure_engine()

        return new_url

    def session(self):
        '''
        Get a SQLAlchemy session for the current connection.

        :return: an instance of :class:`sqlalchemy.orm.session.Session` for the current connection.
        '''
        engine = self.engine()

        if not self._reflected:
            self._reflected = True

            BaseEntity.metadata.create_all(engine)

        if not self._session_class:
            self._session_class = sessionmaker(bind=engine)

        if not self._session:
            self._session = self._session_class()

        return self._session

    def close(self):
        ''' Close the database session. '''
        self._session.close()

        self._session = None

    def post(self, entity):
        '''
        Insert a new `entity` into the database.

        :param `entity`: a new entity.
        '''
        assert isinstance(entity, BaseEntity), 'Expected an entity based on BaseEntity or a declarative base entity.'

        session = self.session()

        session.add(entity)
        session.commit()

    def get(self, entity_type, key):
        '''
        Get an entity of type *entity_type*.

        :param `entity_type`: the class reference of the entities being searched
        :param `key`:         the lookup key
        '''

        session = self.session()
        entity  = session.query(entity_type).get(key)

        return entity

    def get_all(self, entity_type):
        '''
        Get all entities of type *entity_type*.

        :param `entity_type`: the class reference of the entities being searched
        '''

        session = self.session()
        items   = session.query(entity_type).all()

        return items

class EntityService(object):
    def __init__(self, db, kind):
        self._database = db
        self._kind     = kind

    def post(self, *entities):
        session = self._database.session()

        for entity in entities:
            assert isinstance(entity, self._kind),\
                   'Expected an entity of class %s.' % self._kind.__name__

            session.add(entity)

        session.commit()

    def get(self, key):
        return self._database.get(self._kind, key)

    def get_all(self):
        return self._database.get_all(self._kind)