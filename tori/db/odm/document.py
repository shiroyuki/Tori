'''
:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Availability: DEV
:Stability: Stable
'''
from tori.db.odm.exception import LockedIdException, ReservedAttributeException

def document(cls):
    '''
    Decorator to transform normal objects into collection-compatible documents.
    '''
    def get_id(self):
        return self.__dict__['_id'] if '_id' in self.__dict__ else None

    def set_id(self, id):
        '''
        Define the document ID if the original ID is not defined.

        :param id: the ID of the document.
        '''
        if '_id' in self.__dict__ and self.__dict__['_id']:
            raise LockedIdException('The ID is already assigned and cannot be changed.')

        self._id = id

    def get_class_name(self):
        '''
        Retrieve the full type name, include
        '''
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def get_collection_name(self):
        return self.__collection_name__

    def get_changeset(self, get_everything=False):
        changeset      = {}
        changeset_keys = self.__dict__.keys()\
            if   get_everything\
            else self.__dirty_attributes__

        for name in changeset_keys:
            if self.__is_reserved_attribute__(name) or name[0] == '_':
                continue

            changeset[name] = self.__dict__[name] if name in self.__dict__ else None

        if changeset:
            changeset.update({
                '_id':   self.id
            })

        return changeset

    def is_dirty(self, name):
        if name not in self.__dict__:
            raise AttributeError('The attribute "%s" is not found.' % name)

        return self.__in_dirty_bit__(name)

    def reset_bits(self):
        self.__dirty_attributes__ = []

    def __is_method__(self, name):
        return (
            name in dir(self)\
            and callable(self.__getattribute__(name))
        )

    def __is_reserved_attribute__(self, name):
        return (
                name == '_id'\
                and name in self.__dict__
                and self.__dict__[name]
            )\
            or self.__is_method__(name)

    def __in_dirty_bit__(self, name):
        try:
            return name in self.__dirty_attributes__
        except TypeError:
            self.__dirty_attributes__ = []

            return False

    def __mark_dirty_bit__(self, name):
        try:
            self.__dirty_attributes__.append(name)
        except AttributeError:
            print 'B'
            self.__dirty_attributes__ = [name]

    def __setattr__(self, name, value):
        if self.__is_reserved_attribute__(name):
            raise ReservedAttributeException('"%s" is a reserved attribute.' % name)

        object.__setattr__(self, name, value)

        if (
            name != '_id'\
            and name != 'id'\
            and name[0:2] != '__'\
            and not self.__in_dirty_bit__(name)\
            and not self.__is_method__(name)
        ):
            self.__mark_dirty_bit__(name)

    def to_dict(self):
        propertyMap = {
            'id': self.__dict__['_id']
        }

        for name in self.__dict__:
            if name[0] == '_':
                continue

            if callable(self.__dict__[name]):
                continue

            propertyMap[name] = self.__dict__[name]

        return propertyMap

    cls.__setattr__               = __setattr__
    cls.__in_dirty_bit__          = __in_dirty_bit__
    cls.__is_method__             = __is_method__
    cls.__is_reserved_attribute__ = __is_reserved_attribute__
    cls.__mark_dirty_bit__        = __mark_dirty_bit__

    cls.__collection_name__  = cls.__name__.lower()
    cls.__dirty_attributes__ = None

    cls.id                  = property(get_id, set_id)
    cls.get_collection_name = get_collection_name
    cls.get_class_name      = get_class_name
    cls.get_changeset       = get_changeset
    cls.is_dirty            = is_dirty
    cls.reset_bits          = reset_bits
    cls.to_dict             = to_dict

    return cls

class Document(object):
    '''
    Basic document with built-in attribute mapper.
    '''
    def __init__(self, **attributes):
        for name in attributes:
            self.__setattr__(name, attributes[name])