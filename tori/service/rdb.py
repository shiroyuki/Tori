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
        
        return self._session_class()
    
    def post(self, entity):
        '''
        Insert a new `entity` into the database.
        
        :param `entity`: a new entity.
        '''
        if not isinstance(entity, BaseEntity):
            raise InvalidInput, 'Expecting an entity based on BaseEntity or a declarative base entity.'
        
        session = self.session()
        
        session.add(entity)
        session.commit()
        session.close()
    
    def get_all(self, entity_type):
        '''
        Get all entities of type *entity_type*.
        
        :param `entity_type`: the class reference of the entities being searched
        '''
        
        session = self.session(False)
        items   = session.query(entity_type).all()
        
        session.close()
        
        return items

class EntityService(RelationalDatabaseService):
    def __init__(self, url, entity_type):
        RelationalDatabaseService.__init__(self, url)
        
        self._entity_type = entity_type
    
    def get(key):
        session = self.session(False)
        item    = session.query(entity_type).get(key)
        
        session.close()
        
        return item
    
    def get_all(self):
        return super().get_all(self._entity_type)