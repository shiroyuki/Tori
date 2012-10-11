from tori.db.odm.exception import LockedIdException, ReservedAttributeException

class Document(object):
    '''
    Basic document for MongoDB
    '''

    def __init__(self, **attributes):
        for name in attributes:
            self.__dict__[name] = attributes[name]

        self.__dict__['__dirty_attributes__'] = []
        self.__dict__['__collection_name__']  = self.__class__.__name__.lower()

    @property
    def id(self):
        return self.__dict__['_id'] if '_id' in self.__dict__ else None

    @id.setter
    def id(self, id):
        '''
        Define the document ID if the original ID is not defined.

        :param id: the ID of the document.
        '''
        if '_id' in self.__dict__ and self.__dict__['_id']:
            raise LockedIdException('The ID is already assigned and cannot be changed.')

        self.__dict__['_id'] = id

    @property
    def collection_name(self):
        return self.__dict__['__collection_name__']

    def get_class_name(self):
        '''
        Retrieve the full type name, include
        '''
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def is_dirty(self, name):
        if name not in self.__dict__:
            raise AttributeError('The attribute "%s" is not found.' % name)

        return name in self.__dirty_attributes__

    def get_changeset(self):
        changeset = {}

        attribute_names = self.__dict__['__dirty_attributes__'] if self.id else self.__dict__.keys()

        for name in attribute_names:
            if self.__is_reserved_attribute_name(name):
                continue

            changeset[name] = self.__dict__[name]

        if changeset:
            changeset.update({
                '_id':   self.id,
                '_type': self.get_class_name()
            })

        return changeset

    def revert_changes(self):
        self.__dict__['__dirty_attributes__'] = []

    def __is_reserved_attribute_name(self, name):
        return name[0:2] == '__'\
            or name in ['_id', 'collection_name']\
            or (
                name in dir(self)\
                and callable(self.__getattribute__(name))
            )

    def __setattr__(self, name, value):
        if self.__is_reserved_attribute_name(name):
            raise ReservedAttributeException('"%s" is a reserved attribute.' % name)

        object.__setattr__(self, name, value)

        if name not in self.__dict__['__dirty_attributes__']:
            self.__dict__['__dirty_attributes__'].append(name)