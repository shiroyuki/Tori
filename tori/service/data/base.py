from mimetypes import guess_type as get_type
from os        import path as p
from tori.exception import *

class ResourceEntity(object):
    '''
    Static resource entity representing the real static resource which is already loaded to the memory.
    
    :param path: the path to the static resource.
    
    .. note::
        This is for internal use only.
    '''
    def __init__(self, path):
        self.path     = path
        self._content = None
        
        self.type = get_type(path)
        self.type = self.type[0]
    
    def content(self):
        ''' Get the content of the entity. '''
        if self._content:
            return self._content
        
        if not p.exists(self.path):
            return None
        
        with open(self.path) as f:
            self._content = f.read()
        
        return self._content
    
    def set_content(self, new_content):
        '''
        Set the content of the entity.
        
        :param `new_content`: the new content
        '''
        self._content = new_content
    

class ResourceServiceMiddleware(object):
    def __init__(self, *intercepting_mimetypes):
        self._intercepting_mimetypes = intercepting_mimetypes
    
    def expect(self, entity):
        return isinstance(entity, ResourceEntity)\
            and entity.type in self._intercepting_mimetypes
    
    def execute(self, data):
        raise FutureFeatureException, 'This method must be implemented.'