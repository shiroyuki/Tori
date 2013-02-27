"""
Wrappers for SQLAlchemy
#######################

:Author: Juti Noppornpitak
"""
from os import getpid
from threading import current_thread
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tori.common import get_logger

Entity = declarative_base()

class Repository(object):
    """Relational Database Service

    This is compatible with SQLAlchemy 0.7+.

    This service provides basic functionality to interact a relational database.
    It also heavily uses lazy loading for the sake of faster startup and resource
    efficiency.

    :param url: a URL to the database, possibly including location, credential
                and name. The default value is ``sqlite:///:memory:``.
    :type  url: str
    :param echo: the flag to echo database operation. The default value is ``False``
    :type  echo: bool
    """

    def __init__(self, url='sqlite:///:memory:', echo=False):
        self._logger = get_logger('%s.%s' % (__name__, self.__class__.__name__))

        self._echo   = echo
        self._url    = url
        self._engine = None

        self._session_maker      = None
        self._sessions           = {}
        self._batch_reflected    = False
        self._reflected_entities = []

    @property
    def session_key(self):
        return '%s.%s' % (getpid(), current_thread().ident)

    @property
    def engine(self):
        """
        Get the SQLAlchemy engine.

        :rtype: sqlalchemy.engine.base.Engine

        .. note:: With the service, it is not recommended to directly use this method.
        """

        if not self._engine:
            self._engine = create_engine(self._url, echo=self._echo)

        return self._engine

    @property
    def url(self):
        """
        Get the connecting URL.

        :return: the URL
        :rtype: string|unicode
        """
        return self._url

    @url.setter
    def url(self, new_url):
        """
        Set the connecting URL.

        :param new_url: a new URL for the database connection.
        """
        self._url    = new_url
        self._engine = None

    def reflect(self, entity_type=None):
        """
        Create the table if necessary.

        :rtype: True if the reflection is made.
        """
        if not self._batch_reflected and not entity_type:
            self._batch_reflected = True

            Entity.metadata.create_all(self.engine)

            return True

        if self.reflected(entity_type):
            return False

        self._reflected_entities.append(entity_type.__name__)

        try:
            entity_type.__table__.create(self.engine)
        except OperationalError:
            return False

        return True

    def reflected(self, entity_type=None):
        return entity_type.__name__ in self._reflected_entities \
            if entity_type \
            else self._batch_reflected

    @property
    def session(self):
        """
        Get a SQLAlchemy session for the current connection.

        :rtype:  sqlalchemy.orm.session.Session
        :return: a session for the connection.
        """
        engine = self.engine

        if not self._session_maker:
            self._session_maker = sessionmaker(bind=engine)

        session_key = self.session_key

        if session_key not in self._sessions:
            self._logger.info('Create new DB session: %s' % session_key)

            self._sessions[session_key] = self._session_maker()

        return self._sessions[session_key]

    def query(self, *entity_types):
        """
        Retrieve the query object for the given type of entities.

        :param entity_type: the type of entity
        :type entity_type:  list

        :rtype:  sqlalchemy.orm.query.Query
        :return: The query object for the given type of entities.
        """
        for entity_type in entity_types:
            if entity_type.__name__ in self._entity_map:
                continue

            self._entity_map[entity_type.__name__] = True
            entity_type.__table__.create(self.engine)

        return self.session.query(*entity_types)

    def post(self, *entities):
        """
        Insert new `entities` into the database.

        :param entities: a list of new entities.
        """
        session = self.session

        for entity in entities:
            assert isinstance(entity, Entity), 'Expected an entity based on BaseEntity or a declarative base entity.'

            session.add(entity)

        session.commit()
        session.refresh(entity)

    def get(self, entity_type, key):
        """
        Get an entity of type *entity_type*.

        :param entity_type: the class reference of the entities being searched
        :param key:         the lookup key
        """

        return self.query(entity_type).get(key)

    def get_all(self, entity_type):
        """
        Get all entities of type *entity_type*.

        :param entity_type: the class reference of the entities being searched
        """

        return self.query(entity_type).all()