from tori.db.metadata.entity import EntityMetadata

class EntityMetadataHelper(object):
    @staticmethod
    def imprint(cls, collection_name, indexes):
        """ Imprint the entity metadata to the class (type)

            :param cls: the entity class
            :type  cls: type
            :param collection_name: the name of the collection (known as table, bucket etc.)
            :type  collection_name: str
            :param indexes: the list of indexes
            :type  indexes: list
        """
        metadata = EntityMetadata()

        metadata.cls             = cls
        metadata.collection_name = collection_name
        metadata.index_list      = indexes

        cls.__tdbm__ = metadata

    @staticmethod
    def extract(cls):
        return cls.__tdbm__

    @staticmethod
    def hasMetadata(cls):
        return '__tdbm__' in dir(cls)
