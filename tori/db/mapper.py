"""
Mapper
######

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>

This is a module handling object association.

.. note::

    The current implementation doesn't support merging or detaching a document simultaneously observed by at least two
    entity manager.

"""
from imagination.loader import Loader
from tori.db.entity import BasicAssociation
from tori.db.exception import DuplicatedRelationalMapping

dynamic_association_class_template = """
@document({collection_name})
class {class_name}(BasicAssociation): pass
"""

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
    MERGE   = 3 # Not supported in Tori 2.1
    DETACH  = 4 # Not supported in Tori 2.1

class BaseGuide(object):
    def __init__(self, target_class, association):
        self._target_class = target_class
        self.association   = association

    @property
    def target_class(self):
        if isinstance(self._target_class, Loader):
            self._target_class = self._target_class.package

        return self._target_class

class EmbeddingGuide(BaseGuide):
    pass

class RelatingGuide(BaseGuide):
    def __init__(self, target_class, inverted_by, association,
                 read_only, cascading_options):
        BaseGuide.__init__(self, target_class, association)

        self.inverted_by        = inverted_by
        self.read_only          = read_only
        self.cascading_options  = cascading_options

    def association_collection_name(self, entity):
        return '{}_{}'.format(entity.__collection_name__, self.target_class.__collection_name__)

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