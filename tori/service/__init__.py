from tori.decorator.common import singleton
from tori.common           import Loader

class ServiceEntity(object):
    '''
    Service entity
    '''
    
    def __init__(self, id, loader, *args, **kwargs):
        self.__id       = id
        self.__loader   = loader
        self.__args     = args
        self.__kwargs   = kwargs
        self.__instance = None
    
    def id(self):
        return self._id
    
    def loaded(self):
        return self.__instance is not None
    
    def load(self):
        if not self.__instance:
            self.__instance = self.__loader.package()(*self.__args, **self.__kwargs)
        
        return self.__instance

class ServiceLocator(object):
    '''
    Service locator
    '''
    
    __services = {}
    
    def get(self, id):
        try:
            return self.__services[id].load()
        except KeyError:
            raise UnknownServiceError, 'The requested service "%s" is unknown or not found.' % id
    
    def set(self, id, entity):
        self.__services[id] = entity
    
    def has(self, id):
        return id in self.__services