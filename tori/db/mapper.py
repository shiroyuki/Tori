"""
Mapper
######

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>

This is a module handling object association.

.. note::

    The current implementation doesn't support merging or detaching a document simultaneously observed by at least two
    entity manager.

"""
import hashlib
from imagination.loader import Loader
from tori.db.exception import DuplicatedRelationalMapping

class AssociationType(object):
    AUTO_DETECT  = 1 # Not supported in the near future
    ONE_TO_ONE   = 2
    ONE_TO_MANY  = 3
    MANY_TO_ONE  = 4
    MANY_TO_MANY = 5

    @staticmethod
    def known_type(t):
        return AssociationType.AUTO_DETECT <= t <= AssociationType.MANY_TO_MANY

class CascadingType(object):
    PERSIST = 1
    DELETE  = 2
    MERGE   = 3 # Supported in Tori 2.2
    DETACH  = 4 # Supported in Tori 2.2
    REFRESH = 5

class AssociationFactory(object):
    class_name_tmpl      = '{origin_module}{origin}{destination_module}{destination}'
    collection_name_tmpl = '{origin_module}_{origin}_{destination_module}_{destination}'
    code_template        = '\n'.join([
        'from tori.db.entity import BasicAssociation, entity',
        '@entity("{collection_name}")',
        'class {class_name}(BasicAssociation): pass'
    ])

    def __init__(self, origin, destination, cascading_options):
        self.__origin      = origin
        self.__destination = destination
        self.__cascading_options = cascading_options
        self.__class       = None
        self.__class_name  = None
        self.__collection_name = None

    @property
    def class_name(self):
        if not self.__class_name:
            self.__class_name = self.hash_content(self.class_name_tmpl.format(
                origin_module=self.__origin.__module__,
                destination_module=self.__destination.__module__,
                origin=self.__origin.__name__,
                destination=self.__destination.__name__
            ))

            self.__class_name = 'Association{}'.format(self.__class_name)

        return self.__class_name

    @property
    def collection_name(self):
        if not self.__collection_name:
            self.__collection_name = self.hash_content(self.collection_name_tmpl.format(
                origin_module=self.__origin.__module__,
                destination_module=self.__destination.__module__,
                origin=self.__origin.__collection_name__,
                destination=self.__destination.__collection_name__
            ))

        return self.__collection_name

    @property
    def cls(self):
        if not self.__class:
            source = self.code_template.format(
                collection_name=self.collection_name,
                class_name=self.class_name
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
    def __init__(self, target_class, association):
        self._target_class = target_class
        self.association   = association

    @property
    def target_class(self):
        if isinstance(self._target_class, Loader):
            self._target_class = self._target_class.package

        return self._target_class

class EmbeddingGuide(BasicGuide):
    pass

class RelatingGuide(BasicGuide):
    def __init__(self, entity_class, target_class, inverted_by, association,
                 read_only, cascading_options):
        BasicGuide.__init__(self, target_class, association)

        self.inverted_by       = inverted_by
        self.read_only         = read_only
        self.cascading_options = cascading_options

        # This is only used for many-to-many association.
        self.association_class = AssociationFactory(entity_class, self.target_class, cascading_options)\
            if association == AssociationType.MANY_TO_MANY\
            else None

def __prevent_duplicated_mapping(cls, property_name):
    if not cls:
        raise ValueError('Expecting a valid type')

    if property_name in cls.__relational_map__:
        raise DuplicatedRelationalMapping('The property is already mapped.')

def __map_property(cls, property_name, guide):
    cls.__relational_map__[property_name] = guide

def embed(property, target, association_type=AssociationType.AUTO_DETECT):
    def decorator(cls):
        __prevent_duplicated_mapping(cls, property)
        __map_property(cls, property, EmbeddingGuide(target, association_type))
        return cls

    return decorator

def map(cls, mapped_by=None, target=None, inverted_by=None,
        association=AssociationType.AUTO_DETECT, read_only=False,
        cascading=[]):

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
    """Link between two documents

    .. warning:: This is experimental for Tori 2.1

    :param mapped_by:   the name of property of the current class
    :param target:      the target class or class name (e.g., acme.entity.User)
    :param inverted_by: the name of property of the target class
    :param association: the type of association
    :param read_only:   the flag to indicate whether this is for read only.
    :param cascading:   the list of actions on cascading

    :return: the decorator callback

    If :param:`target` is not defined, the default target will be the reference class.

    ``on_delete`` will be only used if cascading is required on deletion.
    """
    def decorator(cls):
        map(cls, mapped_by, target, inverted_by, association, read_only, cascading)

        return cls

    return decorator