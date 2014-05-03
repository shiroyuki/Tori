class ReadOnlyEntityMetadataException(Exception): pass

class EntityMetadata(object):
    def __init__(self):
        self._locked = True # the metadata is read-only.

        self._collection_name = None
        self._index_list      = []
        self._relational_map  = {}

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        if self._collection_name and self._locked:
            raise ReadOnlyEntityMetadataException('The class metadata is read-only.')

        self._collection_name = value

    @property
    def relational_map(self):
        return self._relational_map

    @relational_map.setter
    def relational_map(self, value):
        if self._relational_map and self._locked:
            raise ReadOnlyEntityMetadataException('The class metadata is read-only.')

        self._relational_map = value

    @property
    def index_list(self):
        return self._index_list
    @index_list.setter
    def index_list(self, value):
        if self._index_list and self._locked:
            raise ReadOnlyEntityMetadataException('The class metadata is read-only.')

        self._index_list = value


