from mimetypes import guess_type as get_type
from os        import path as p
from imagination.helper import retrieve_module_path
from tori.exception import *

module_path_map = {}

def resolve_file_path(file_path):
    if ':' not in file_path:
        return file_path

    module_name, relative_path = file_path.split(':')

    if module_name in module_path_map:
        module_path = module_path_map[module_name]
    else:
        module_path = retrieve_module_path(module_name)

        module_path_map[module_name] = module_path

    return p.join(module_path, relative_path)

class ResourceEntity(object):
    """
    Static resource entity representing the real static resource which is already loaded to the memory.

    :param path: the path to the static resource.

    .. note::
        This is for internal use only.
    """

    DEFAULT_INDEX_FILE = 'index.html'

    def __init__(self, path, cacheable=False):
        accessible_path = resolve_file_path(path)

        self._is_originally_dir = p.isdir(accessible_path)

        if self._is_originally_dir:
            accessible_path = p.join(accessible_path, ResourceEntity.DEFAULT_INDEX_FILE)

        self._path      = accessible_path
        self._content   = None
        self._cacheable = cacheable

        self._type = get_type(accessible_path)
        self._type = self.kind[0]

    @property
    def original_request_path(self):
        return self._original_request_path
    @original_request_path.setter
    def original_request_path(self, value):
        self._original_request_path = value

    @property
    def is_originally_dir(self):
        return self._is_originally_dir

    @is_originally_dir.setter
    def is_originally_dir(self, value):
        self._is_originally_dir = value

    @property
    def kind(self):
        return self._type

    @property
    def path(self):
        return self._path

    @property
    def exists(self):
        return p.exists(self.path)

    @property
    def content(self):
        """ Get the content of the entity. """
        if self._content:
            return self._content

        if not self.exists:
            return None

        try:
            with open(self.path, 'r') as f:
                self._content = f.read()
        except UnicodeDecodeError as e:
            with open(self.path, 'rb') as f:
                self._content = f.read()

        f.close()

        return self._content

    @content.setter
    def content(self, new_content):
        """
        Set the content of the entity.

        :param `new_content`: the new content
        """
        self._content = new_content

    @property
    def cacheable(self):
        return self._cacheable


class ResourceServiceMiddleware(object):
    def __init__(self, *intercepting_mimetypes):
        self._intercepting_mimetypes = intercepting_mimetypes

    def expect(self, entity):
        return isinstance(entity, ResourceEntity)\
            and entity.kind in self._intercepting_mimetypes

    def execute(self, data):
        raise FutureFeatureException('This method must be implemented.')