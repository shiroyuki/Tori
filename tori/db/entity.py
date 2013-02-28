"""
Document
========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Stability: Stable

This module contains the abstract of documents in MongoDB.
"""
import inspect
from tori.db.common import PseudoObjectId

from tori.db.exception import LockedIdException

def entity(*args, **kwargs):
    """Document decorator

    :param collection_name: the name of the collection
    :type collection_name: str
    :return: the decorated object
    :rtype: str
    """
    # Get the first parameter.
    first_param = args[0]

    # If the first parameter is really a reference to a class, then instantiate
    # the singleton instance.
    if len(args) == 1 and inspect.isclass(first_param) and isinstance(first_param, type):
        class_reference = first_param

        return prepare_entity_class(class_reference)

    # Otherwise, use the closure to handle the parameter.
    def decorator(class_reference):
        return prepare_entity_class(class_reference, *args, **kwargs)

    return decorator

def prepare_entity_class(cls, collection_name=None):
    """Create a document-type class

    :param cls: the document class
    :type cls: object

    The object decorated with this decorator will be provided with the following read-only attribute

    ========= ===================
    Attribute Description
    ========= ===================
    id        Document Identifier
    ========= ===================

    and methods

    =================== ========================================================
    Method              Description
    =================== ========================================================
    get_collection_name Get the default name of the collection
    get_class_name      Get the default name of the class
    get_changeset       Get the computed changeset
    is_dirty            Check if a certain attribute is dirty (changed or added)
    reset_bits          Reset the computed changeset
    to_dict             Convert the data into dictionary (experimental)
    =================== ========================================================

    .. note::

        Internally, the attribute ``_id`` of the decorated object holds the object identifier (ID). Although it is
        writeable and accessible publicly, it is strongly discouraged from accessing the property directly AFTER the
        instantiation.

    Here is an example.

    .. code-block:: python

        @document
        class Note(object):
            def __init__(self, title, author, content, _id=None):
                self.title   = title
                self.author  = author
                self.content = content
                self._id     = _id

    From the example, you will notice that this is all it take to make it work with :class:`tori.db.repository.Repository`.

    You will also see that this example tell the constructor to set ``_id``. This is just to work with the collection API.
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
        if '_id' in self.__dict__ and self.__dict__['_id'] and not isinstance(self.__dict__['_id'], PseudoObjectId):
            raise LockedIdException('The ID is already assigned and cannot be changed.')

        self._id = id

    cls.__collection_name__ = collection_name or cls.__name__.lower()
    cls.__relational_map__  = {}
    cls.__session__         = None

    cls.id = property(get_id, set_id)

    return cls

class Entity(object):
    """Dynamic-attribute Base Document

    :param attributes: key-value dictionary
    :type attributes: dict

    Here is the example on how to use this class.

    .. code-block:: python

        @document
        class Note(Entity): pass

    In this case, it is similar to the example for :py:meth:`document` except that the class ``DependencyNode`` no longer guarantees
    that it will have attributes ``title``, ``content`` and ``author`` but it maps all available data to the object.

    In case that a document class needs to have certain attributes and unknown dynamic attributes the Note class should
    look like this.

    .. code-block:: python

        @document
        class Note(Entity):
            def __init__(self, title, author, content, **attributes):
                Entity.__init__(self, **attributes)

                self.title   = title
                self.author  = author
                self.content = content
    """
    def __init__(self, **attributes):
        for name in attributes:
            self.__setattr__(name, attributes[name])

class BasicAssociation(object):
    def __init__(self, origin, destination):
        self.origin      = origin
        self.destination = destination