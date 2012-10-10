class LockedIdException(Exception):
    ''' Exception thrown when the ID is tempted to change. '''

class ReservedAttributeException(Exception):
    ''' Exception thrown when a reserved attribute is tempted to change. '''