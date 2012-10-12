class CollectionUnavailable(Exception):
    ''' Exception thrown when the collection is not available. '''

class LockedIdException(Exception):
    ''' Exception thrown when the ID is tempted to change. '''

class ReservedAttributeException(Exception):
    ''' Exception thrown when a reserved attribute is tempted to change. '''