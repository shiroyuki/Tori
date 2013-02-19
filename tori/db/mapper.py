"""
Mapper
######

:Author: Juti Noppornpitak <jnopporn@shiroyuki.com>

This is a module handling object association.

.. note::

    The current implementation doesn't support merging or detaching a document simultaneously observed by at least two
    entity manager.

"""

from tori.db.exception import DuplicatedRelationalMapping

class AssociationType(object):
    AUTO_DETECT  = 1
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
    def __init__(self, target_class, association_type):
        self.target_class = target_class
        self.association_type = association_type

class EmbeddingGuide(BaseGuide):
    pass

class RelatingGuide(BaseGuide):
    def __init__(self, target_class, is_reverse_mapping, association_type,
                 read_only, cascading_options):
        BaseGuide.__init__(self, target_class, association_type)

        self.is_reverse_mapping = is_reverse_mapping
        self.read_only          = read_only
        self.cascading_options  = cascading_options

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

def link(mapped_by=None, target=None, inverted_by=None,
         association_type=AssociationType.AUTO_DETECT, read_only=False,
         cascading=[]):
    """Link between two documents

    .. warning:: This is experimental for Tori 2.1

    :param mapped_by:        the name of property of the current class
    :param target:           the target class
    :param inverted_by:      the name of property of the target class
    :param association_type: the type of association
    :param read_only:        the flag to indicate whether this is for read only.

    :return: the decorator callback

    If :param:`target` is not defined, the default target will be the reference class.
    """

    if association_type == AssociationType.AUTO_DETECT:
        raise ValueError('The association is not specified.')

    if not AssociationType.known_type(association_type):
        raise ValueError('Unknown association')

    def decorator(cls):
        mapped_property_name = inverted_by
        is_reverse_mapping   = True

        if mapped_by:
            mapped_property_name = mapped_by
            is_reverse_mapping   = False

        __prevent_duplicated_mapping(cls, mapped_by)
        __map_property(
            cls,
            mapped_property_name,
            RelatingGuide(
                target or cls,
                is_reverse_mapping,
                association_type,
                read_only,
                cascading
            )
        )

        return cls

    return decorator