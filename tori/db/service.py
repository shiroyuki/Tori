# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitak

The default relational database service for Tori framework compatible with SQLAlchemy.
'''

from os        import getpid
from threading import current_thread

from sqlalchemy     import create_engine
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import sessionmaker

from tori.common    import getLogger
from tori.exception import *

from tori.db.entity import Entity as BaseEntity

class RelationalDatabaseService(object):
    '''
    Relational Database Service based on SQLAlchemy 0.7+

    This service provides basic functionality to interact a relational database.
    It also heavily uses lazy loading for the sake of faster startup and resource
    efficiency.

    :param url: a URL to the database, possibly including location, credential
                and name. The default value is ``sqlite:///:memory:``.
    '''

    def __init__(self, url='sqlite:///:memory:', echo=False):
        self._logger = getLogger('%s.%s' % (__name__, self.__class__.__name__))

        self._echo          = echo
        self._engine        = None
        self._url           = url
        self._reflected     = False
        self._session_maker = None
        self._sessions      = {}

    @property
    def session_key(self):
        return '%s.%s' % (getpid(), current_thread().ident)

    @property
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
        self._engine = create_engine(self._url, echo=self._echo)

    @property
    def url(self):
        '''
        Get the connecting URL.

        :return: the URL
        :rtype: string|unicode
        '''
        return self._url

    @url.setter
    def url(self, new_url):
        '''
        Set the connecting URL.

        :param new_url: a new URL for the database connection.
        '''
        self._url = new_url

        self._configure_engine()

    @property
    def session(self):
        '''
        Get a SQLAlchemy session for the current connection.

        :return: an instance of :class:`sqlalchemy.orm.session.Session` for the current connection.
        '''
        engine = self.engine

        if not self._reflected:
            self._reflected = True

            BaseEntity.metadata.create_all(engine)

        if not self._session_maker:
            self._session_maker = sessionmaker(bind=engine)

        session_key = self.session_key

        if session_key not in self._sessions:
            self._logger.info('Create new DB session: %s' % session_key)

            self._sessions[session_key] = self._session_maker()

        return self._sessions[session_key]

    def query(self, entity_type):
        return self.session.query(entity_type)

    def post(self, *entities):
        '''
        Insert new `entities` into the database.

        :param entities: a list of new entities.
        '''
        session = self.session

        for entity in entities:
            assert isinstance(entity, BaseEntity), 'Expected an entity based on BaseEntity or a declarative base entity.'

            session.add(entity)

        session.commit()
        session.refresh(entity)

    def get(self, entity_type, key):
        '''
        Get an entity of type *entity_type*.

        :param entity_type: the class reference of the entities being searched
        :param key:         the lookup key
        '''

        return self.query(entity_type).get(key)

    def get_all(self, entity_type):
        '''
        Get all entities of type *entity_type*.

        :param entity_type: the class reference of the entities being searched
        '''

        return self.query(entity_type).all()