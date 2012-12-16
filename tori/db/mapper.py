from exception import DuplicatedRelationalMapping

class AssociationType(object):
    AUTO_DETECT  = 1
    ONE_TO_ONE   = 2
    ONE_TO_MANY  = 3
    MANY_TO_ONE  = 4
    MANY_TO_MANY = 5

    @staticmethod
    def known_type(t):
        return AssociationType.AUTO_DETECT <= t <= AssociationType.MANY_TO_MANY

class BaseGuide(object):
    def __init__(self, target, association_type):
        self.target = target
        self.association_type = association_type

class EmbeddingGuide(BaseGuide):
    pass

class RelatingGuide(BaseGuide):
    def __init__(self, target, target_property, association_type):
        BaseGuide.__init__(self, target, association_type)

        self.target_property = target_property

def __prevent_duplicated_mapping(cls, property_name):
    if '__relational_map__' not in cls.__dict__:
        cls.__relational_map__ = {}

        return

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

def link(property, target, target_property, association_type=AssociationType.AUTO_DETECT):
    """Link between two documents

    .. warning:: This is experimental for Tori 2.1

    :param property:         the name of property of the current class
    :param target:           the target class
    :param target_property:  the name of property of the target class
    :param association_type: the type of association

    :return: the decorator callback
    """
    def decorator(cls):
        __prevent_duplicated_mapping(cls, property)
        __map_property(cls, property, RelatingGuide(target, target_property, association_type))

    return decorator