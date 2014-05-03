"""
:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
"""
import inspect
from imagination.decorator.validator import restrict_type
from tori.db.common    import PseudoObjectId
from tori.db.exception import LockedIdException
from tori.db.metadata.helper import EntityMetadataHelper

def get_collection_name(cls):
    raise RuntimeError('obsolete')
    return cls.__collection_name__

def get_relational_map(cls):
    raise RuntimeError('obsolete')
    return cls.__relational_map__

def entity(*args, **kwargs):
    """ Entity decorator

        :param collection_name: the name of the collection
        :type  collection_name: str
        :return: the decorated object
        :rtype:  object
    """
    # Get the first parameter.
    first_param = args[0] if args else None

    # If the first parameter is really a reference to a class, then instantiate
    # the singleton instance.
    if args and inspect.isclass(first_param) and isinstance(first_param, type):
        class_reference = first_param

        return prepare_entity_class(class_reference)

    # Otherwise, use the closure to handle the parameter.
    def decorator(class_reference):
        return prepare_entity_class(class_reference, *args, **kwargs)

    return decorator

def prepare_entity_class(cls, collection_name=None, indexes=[]):
    """ Create a entity class

    :param cls: the document class
    :type  cls: object
    :param collection_name: the name of the corresponding collection where the
                            default is the lowercase version of the name of the
                            given class (cls)
    :type  collection_name: str

    The object decorated with this decorator will be automatically provided with
    a few additional attributes.

    =================== ======== =================== ==== =================================
    Attribute           Access   Description         Read Write
    =================== ======== =================== ==== =================================
    id                  Instance Document Identifier Yes  Yes, ONLY ``id`` is undefined.
    __t3_orm_meta__     Static   Tori 3's Metadata   Yes  ONLY the property of the metadata
    __session__         Instance DB Session          Yes  Yes, but NOT recommended.
    =================== ======== =================== ==== =================================

    The following attributes might stay around but are deprecated as soon as
    the stable Tori 3.0 is released.

    =================== ======== =================== ==== =================================
    Attribute           Access   Description         Read Write
    =================== ======== =================== ==== =================================
    __collection_name__ Static   Collection Name     Yes  Yes, but NOT recommended.
    __relational_map__  Static   Relational Map      Yes  Yes, but NOT recommended.
    __indexes__         Static   Indexing List       Yes  Yes, but NOT recommended.
    =================== ======== =================== ==== =================================

    ``__session__`` is used to resolve the managing rights in case of using
    multiple sessions simutaneously.

    For example,

    .. code-block:: python

        @entity
        class Note(object):
            def __init__(self, content, title=''):
                self.content = content
                self.title   = title

    where the collection name is automatically defined as "note".

    .. versionchanged:: 3.0

        The way Tori stores metadata objects in ``__collection_name__``,
        ``__relational_map__`` and ``__indexes__`` are now ignored by the ORM
        in favour of ``__t3_orm_meta__`` which is an entity metadata object.

        This change is made to allow easier future development.

    .. tip::

        You can define it as "notes" by replacing ``@entity`` with ``@entity('notes')``.
    """
    if not cls:
        raise ValueError('Expecting a valid type')

    def get_id(self):
        return self.__dict__['_id'] if '_id' in self.__dict__ else None

    def set_id(self, id):
        """
        Define the document ID if the original ID is not defined.

        :param id: the ID of the document.
        """
        if '_id' in self.__dict__ and self.__dict__['_id']\
            and not isinstance(self.__dict__['_id'], PseudoObjectId):
            raise LockedIdException('The ID is already assigned and cannot be changed.')

        self._id = id

    cls.__session__ = None

    EntityMetadataHelper.imprint(
        cls,
        collection_name or cls.__name__.lower(),
        indexes
    )

    cls.id = property(get_id, set_id)

    return cls

class Entity(object):
    """ Dynamic-attribute Basic Entity

        :param attributes: key-value dictionary
        :type  attributes: dict

        Here is an example on how to use this class.

        .. code-block:: python

            @entity
            class Note(Entity): pass

    """
    def __init__(self, **attributes):
        for name in attributes:
            self.__setattr__(name, attributes[name])

class Index(object):
    """ Index

        :param field_map: the map of field to index type
        :type  field_map: dict
        :param unique: the unique flag
        :type  unique: bool

        Unless a field is not in the map of fixed orders, the index will
        instruct the repository to ensure all combinations of indexes are
        defined whenever is necessary.
    """
    def __init__(self, field_map, unique=False):
        self._field_map = field_map
        self._unique    = unique

    @property
    def field_map(self):
        return self._field_map

    @property
    def unique(self):
        return self._unique

    def to_list(self):
        index_map = []

        for field in self._field_map:
            index_map.append((field, self._field_map[field]))

        return index_map

class BasicAssociation(object):
    """ Basic Association

        :param origin: The origin of the association
        :type  origin: object
        :param destination: The destination (endpoint) of the association
        :type  destination: object

        .. note:: This class is used automatically by the association mapper.
    """
    def __init__(self, origin, destination):
        self.origin      = origin
        self.destination = destination