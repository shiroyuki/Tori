'''
:Author: Juti Noppornpitak

Service
'''

from tori.common    import Console, Loader
from tori.exception import *

class ServiceEntity(object):
    '''
    Service entity
    
    *id* is the service identifier (string).
    
    *loader* is a service loader which is an instance of :class:`tori.common.Loader`.
    
    *args* and *kwargs* are parameters used to instantiate the service.
    
    If the loader is not an instance of :class:`tori.common.Loader` or any classes based on :class:`tori.common.Loader`,
    the exception :class:`tori.exception.InvalidInput` will be thrown.
    '''
    
    def __init__(self, id, loader, *args, **kwargs):
        if not isinstance(loader, Loader):
            raise InvalidInput, 'Expected a service loader.'
        
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
            Console.log('Instantiated the service "%s".' % self.__id)
        
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
        Console.log('Set the service "%s".' % id)
        self.__services[id] = entity
    
    def has(self, id):
        return id in self.__services