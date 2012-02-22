'''
:Author: Juti Noppornpitak

The default relational database service for Tori framework.
'''

from sqlalchemy                 import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker

from tori.exception             import *

BaseEntity = declarative_base()

class RelationalDatabaseService(object):
    '''
    This service provides basic functionality to interact a relational database.
    
    This service heavily uses lazy loading for the sake of faster startup and resource efficiency.
    
    *url* is a URL to the database, possibly including location, credential and name.
    '''
    def __init__(self, url):    
        self._engine   = None
        self._url      = url
        self._session  = None
        self._reflected = False
    
    def engine(self):
        '''
        Get the SQLAlchemy engine.
        
        .. note::
            With the service, it is not recommended to directly use this method.
        '''
        if not self._engine:
            self._engine = create_engine(self._url, echo=False)
        
        return self._engine
    
    def session(self):
        '''
        Get a SQLAlchemy session.
        
        .. note::
            With the service, it is not recommended to directly use this method.
        '''
        engine = self.engine()
        
        if not self._reflected:
            self._reflected = True
            
            BaseEntity.metadata.create_all(engine)
        
        if not self._session:
            self._session = sessionmaker(bind=engine)
        
        return self._session()
    
    def commit(self):
        ''' Manually commit the changes. '''
        self.session().commit()
    
    def post(self, entity, auto_commit=True):
        '''
        Post an given entity as a new entity.
        
        *entity* is a new entity.
        
        *auto_commit* is to indicate whether the method should commit this change automatically.
        '''
        if not isinstance(entity, BaseEntity):
            raise InvalidInput, 'Expecting an entity based on BaseEntity or a declarative base entity.'
        
        db = self.session()
        
        db.add(entity)
        
        if auto_commit:
            db.commit()
    
    def _get_all(self, entity_type):
        ''' Get all entities of type *entity_type*. '''
        return self.session().query(entity_type).all()

class EntityService(RelationalDatabaseService):
    def __init__(self, url, entity_type):
        super(self.__class__, self).__init__(url)
        
        self._entity_type = entity_type
    
    def get_all(self):
        return self._get_all(self._entity_type)