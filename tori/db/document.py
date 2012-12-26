"""
Document
========

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>
:Stability: Stable

This module contains the abstract of documents in MongoDB.
"""
import inspect

from tori.db.exception import LockedIdException, ReservedAttributeException
from tori.db.mapper import AssociationType, EmbeddingGuide

def document(*args, **kwargs):
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

        return make_document_class(class_reference)

    # Otherwise, use the closure to handle the parameter.
    def decorator(class_reference):
        return make_document_class(class_reference, *args, **kwargs)

    return decorator

def make_document_class(cls, collection_name=None):
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

    From the example, you will notice that this is all it take to make it work with :class:`tori.db.collection.Collection`.

    You will also see that this example tell the constructor to set ``_id``. This is just to work with the collection API.
    """
    def get_id(self):
        return self.__dict__['_id'] if '_id' in self.__dict__ else None

    def set_id(self, id):
        """
        Define the document ID if the original ID is not defined.

        :param id: the ID of the document.
        """
        if '_id' in self.__dict__ and self.__dict__['_id']:
            raise LockedIdException('The ID is already assigned and cannot be changed.')

        self._id = id

    def __is_reserved_attribute__(self, name):
        is_identifier_defined = (
            name == '_id'\
            and name in self.__dict__
            and self.__dict__[name]
            )

        return is_identifier_defined or self.__is_method__(name)

    def __is_observable_property__(self, name):
        is_not_identifier = name not in ['_id', 'id']
        is_readonly       = name[0:2] != '__' and not self.__is_method__(name)

        return is_not_identifier and is_readonly and not self.__in_dirty_bit__(name)

    def get_class_name(self):
        """
        Retrieve the full type name, include
        """
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

            new_value = self.__dict__[name] if name in self.__dict__ else None

            # Recursively
            if 'get_changeset' in dir(new_value):
                new_value = new_value.get_changeset()
            elif type(new_value) is list:
                items     = new_value
                new_value = []

                for item in items:
                    if 'get_changeset' in dir(item):
                        new_value.append(item.get_changeset())

            changeset[name] = new_value

        if changeset:
            changeset.update({
                '_id': self.id
            })

        if not self.id:
            del changeset['_id']

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
            self.__dirty_attributes__ = [name]

    def __setattr__(self, name, value):
        if self.__is_reserved_attribute__(name):
            raise ReservedAttributeException('"%s" is a reserved attribute.' % name)

        if name in self.__dict__ and self.__dict__[name] == value:
            return

        relationship = self.__relational_map__[name] if name in self.__relational_map__ else None
        """ :type: tori.db.mapper.BaseGuide """

        # Automatically convert the data for embedded-object-mapped property.
        if relationship and type(relationship) is EmbeddingGuide:
            association_type = relationship.association_type

            if association_type == AssociationType.AUTO_DETECT:
                if type(value) is dict:
                    association_type = AssociationType.ONE_TO_ONE
                elif type(value) is list:
                    association_type = AssociationType.ONE_TO_MANY

            if association_type == AssociationType.ONE_TO_ONE:
                value = value if isinstance(value, relationship.target) else relationship.target(**value)
            elif association_type == AssociationType.ONE_TO_MANY:
                data_list = list(value)
                value     = []

                for data in data_list:
                    embedded_object = data if isinstance(data, relationship.target) else relationship.target(**data)

                    value.append(embedded_object)

        object.__setattr__(self, name, value)

        if self.__is_observable_property__(name):
            self.__mark_dirty_bit__(name)

    cls.__setattr__                = __setattr__
    cls.__in_dirty_bit__           = __in_dirty_bit__
    cls.__is_method__              = __is_method__
    cls.__is_reserved_attribute__  = __is_reserved_attribute__
    cls.__mark_dirty_bit__         = __mark_dirty_bit__
    cls.__is_observable_property__ = __is_observable_property__

    cls.__collection_name__  = collection_name or cls.__name__.lower()
    cls.__dirty_attributes__ = None

    if '__relational_map__' not in cls.__dict__:
        cls.__relational_map__ = {}

    cls.id                  = property(get_id, set_id)
    cls.get_collection_name = get_collection_name
    cls.get_class_name      = get_class_name
    cls.get_changeset       = get_changeset
    cls.is_dirty            = is_dirty
    cls.reset_bits          = reset_bits

    return cls

class BaseDocument(object):
    """Dynamic-attribute Base Document

    :param attributes: key-value dictionary
    :type attributes: dict

    Here is the example on how to use this class.

    .. code-block:: python

        @document
        class Note(BaseDocument): pass

    In this case, it is similar to the example for :py:meth:`document` except that the class ``Node`` no longer guarantees
    that it will have attributes ``title``, ``content`` and ``author`` but it maps all available data to the object.

    In case that a document class needs to have certain attributes and unknown dynamic attributes the Note class should
    look like this.

    .. code-block:: python

        @document
        class Note(BaseDocument):
            def __init__(self, title, author, content, **attributes):
                BaseDocument.__init__(self, **attributes)

                self.title   = title
                self.author  = author
                self.content = content
    """
    def __init__(self, **attributes):
        for name in attributes:
            self.__setattr__(name, attributes[name])