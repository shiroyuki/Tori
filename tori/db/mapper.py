# -*- coding: utf-8 -*-
"""
.. note::

    The current implementation doesn't support merging or detaching a document
    simultaneously observed by at least two entity manager.

"""
import hashlib
from imagination.loader import Loader
from tori.db.exception import DuplicatedRelationalMapping
from tori.db.metadata.helper import EntityMetadataHelper

class AssociationType(object):
    """ Association Type """
    AUTO_DETECT  = 1 # Not supported in the near future
    """ Auto detection (default, disabled and raising exception) """
    ONE_TO_ONE   = 2
    """ One-to-one association mode """
    ONE_TO_MANY  = 3
    """ One-to-many association mode """
    MANY_TO_ONE  = 4
    """ Many-to-one association mode """
    MANY_TO_MANY = 5
    """ Many-to-many association mode """

    @staticmethod
    def known_type(t):
        """ Check if it is a known type

            :param t: type
            :type  t: int
            :returns: ``True`` if it is a known type.
            :rtype: bool
        """
        return AssociationType.AUTO_DETECT <= t <= AssociationType.MANY_TO_MANY

class CascadingType(object):
    """ Cascading Type """
    PERSIST = 1
    """ Cascade on persist operation """
    DELETE  = 2
    """ Cascade on delete operation """
    MERGE   = 3
    """ Cascade on merge operation

        .. note:: Supported in Tori 2.2
    """
    DETACH  = 4 # Supported in Tori 2.2
    """ Cascade on detach operation

        .. note:: Supported in Tori 2.2
    """
    REFRESH = 5
    """ Cascade on refresh operation """

class AssociationFactory(object):
    """ Association Factory """
    class_name_tmpl      = '{origin_module}{origin}{destination_module}{destination}'
    collection_name_tmpl = '{origin}_{destination}'
    code_template        = '\n'.join([
        'from tori.db.entity import BasicAssociation, entity',
        '@entity("{collection_name}")',
        'class {class_name}(BasicAssociation): pass'
    ])

    def __init__(self, origin, guide, cascading_options, is_reverse_mapping):
        self.__is_reverse_mapping = is_reverse_mapping
        self.__origin      = origin
        self.__guide       = guide
        self.__destination = None
        self.__cascading_options = cascading_options
        self.__class       = None
        self.__class_name  = None
        self.__collection_name = None

        if is_reverse_mapping:
            self.__origin      = None
            self.__destination = origin
            self.__cascading_options = []

    @property
    def origin(self):
        """ Origin

            :rtype: type
        """
        if not self.__origin:
            self.__origin = self.__guide.target_class

        return self.__origin

    @property
    def destination(self):
        """ Destination

            :rtype: type
        """
        if not self.__destination:
            self.__destination = self.__guide.target_class

        return self.__destination

    @property
    def class_name(self):
        """ Auto-generated Association Class Name

            :rtype: str

            .. note:: This is a read-only property.
        """
        if not self.__class_name:
            self.__class_name = self.hash_content(self.class_name_tmpl.format(
                origin_module      = self.origin.__module__,
                destination_module = self.destination.__module__,
                origin             = self.origin.__name__,
                destination        = self.destination.__name__
            ))

            self.__class_name = 'Association{}'.format(self.__class_name)

        return self.__class_name

    @property
    def collection_name(self):
        """ Auto-generated Collection Name

            :rtype: str

            .. note:: This is a read-only property.
        """
        if not self.__collection_name:
            self.__collection_name = self.collection_name_tmpl.format(
                origin      = EntityMetadataHelper.extract(self.origin).collection_name,
                destination = EntityMetadataHelper.extract(self.destination).collection_name
            )

        return self.__collection_name

    @property
    def cls(self):
        """ Auto-generated Association Class

            :rtype: type

            .. note:: This is a read-only property.
        """
        if not self.__class:
            source = self.code_template.format(
                collection_name = self.collection_name,
                class_name      = self.class_name
            )

            code = compile(source, '<string>', 'exec')

            exec(code, globals())

            if self.class_name in globals():
                self.__class = globals()[self.class_name]
            else:
                raise RuntimeError('Unable to auto-generation associative collection class.')

        return self.__class

    def hash_content(self, content):
        return hashlib.sha224(content.encode('ascii')).hexdigest()

class BasicGuide(object):
    """ Basic Relation Guide

        This class is abstract and used with the relational map of the given entity class.

        :param target_class: the target class or class name (e.g., acme.entity.User)
        :type  target_class: object
        :param association:  the type of association
        :type  association:  int
    """
    def __init__(self, target_class, association):
        self._target_class = target_class
        self.association   = association

    @property
    def target_class(self):
        """ The target class

            :rtype: type
        """
        if isinstance(self._target_class, Loader):
            self._target_class = self._target_class.package

        return self._target_class

class RelatingGuide(BasicGuide):
    """ Relation Guide

        This class is used with the relational map of the given entity class.

        :param entity_class: the reference of the current class
        :type  entity_class: type
        :param mapped_by:    the name of property of the current class
        :type  mapped_by:    str
        :param target_class: the target class or class name (e.g., acme.entity.User)
        :type  target_class: type
        :param inverted_by:  the name of property of the target class
        :type  inverted_by:  str
        :param association:  the type of association
        :type  association:  int
        :param read_only:    the flag to indicate whether this is for read only.
        :type  read_only:    bool
        :param cascading_options: the list of actions on cascading
        :type  cascading_options: list or tuple
    """
    def __init__(self, entity_class, target_class, inverted_by, association,
                 read_only, cascading_options):
        BasicGuide.__init__(self, target_class, association)

        self.origin_class      = entity_class
        self.inverted_by       = inverted_by
        self.read_only         = read_only
        self.cascading_options = cascading_options

        # This is only used for many-to-many association.
        self.association_class = AssociationFactory(
                entity_class,
                self,
                cascading_options,
                self.inverted_by != None
            )\
            if association == AssociationType.MANY_TO_MANY\
            else None

def __prevent_duplicated_mapping(cls, property_name):
    if not cls:
        raise ValueError('Expecting a valid type')

    metadata = EntityMetadataHelper.extract(cls)

    if property_name in metadata.relational_map:
        raise DuplicatedRelationalMapping('The property is already mapped.')

def __map_property(cls, property_name, guide):
    metadata = EntityMetadataHelper.extract(cls)

    metadata.relational_map[property_name] = guide

def map(cls, mapped_by=None, target=None, inverted_by=None,
        association=AssociationType.AUTO_DETECT, read_only=False,
        cascading=[]):
    """ Map the given class property to the target class.

        .. versionadded:: 2.1

        :param cls:         the reference of the current class
        :type  cls:         type
        :param mapped_by:   the name of property of the current class
        :type  mapped_by:   str
        :param target:      the target class or class name (e.g., acme.entity.User)
        :type  target:      type
        :param inverted_by: the name of property of the target class
        :type  inverted_by: str
        :param association: the type of association
        :type  association: int
        :param read_only:   the flag to indicate whether this is for read only.
        :type  read_only:   bool
        :param cascading:   the list of actions on cascading
        :type  cascading:   list or tuple
    """

    if association == AssociationType.AUTO_DETECT:
        raise ValueError('The association is not specified.')

    if not AssociationType.known_type(association):
        raise ValueError('Unknown association')

    # Allow a name of classes as a target (e.g., acme.entity.User or 'acme.entity.User')
    if isinstance(target, str):
        loader = Loader(target)
        target = loader

    __prevent_duplicated_mapping(cls, mapped_by)
    __map_property(
        cls,
        mapped_by,
        RelatingGuide(
            cls,
            target or cls,
            inverted_by,
            association,
            read_only,
            cascading
        )
    )

def link(mapped_by=None, target=None, inverted_by=None,
         association=AssociationType.AUTO_DETECT, read_only=False,
         cascading=[]):
    """ Association decorator

        .. versionadded:: 2.1

        This is to map a property of the current class to the target class.

        :param mapped_by:   the name of property of the current class
        :type  mapped_by:   str
        :param target:      the target class or class name (e.g., acme.entity.User)
        :type  target:      type
        :param inverted_by: the name of property of the target class
        :type  inverted_by: str
        :param association: the type of association
        :type  association: int
        :param read_only:   the flag to indicate whether this is for read only.
        :type  read_only:   bool
        :param cascading:   the list of actions on cascading
        :type  cascading:   list or tuple

        :return: the decorated class
        :rtype:  type

        .. tip:: If ``target`` is not defined, the default target will be the reference class.
    """
    def decorator(cls):
        map(cls, mapped_by, target, inverted_by, association, read_only, cascading)

        return cls

    return decorator