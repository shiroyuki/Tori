class DuplicatedRelationalMapping(Exception):
    """ Exception thrown when the property is already mapped. """

class UnavailableCollectionException(Exception):
    """ Exception thrown when the collection is not available. """

class LockedIdException(Exception):
    """ Exception thrown when the ID is tempted to change. """

class ReservedAttributeException(Exception):
    """ Exception thrown when a reserved attribute is tempted to change. """

class UOWRepeatedRegistrationError(IOError):
    """ Error thrown when the given reference is already registered as a new reference or already existed. """

class UOWUnknownRecordError(IOError):
    """ Error thrown when the given reference is already registered as a new reference or already existed. """

class UOWUpdateError(IOError):
    """ Error thrown when the given reference is already registered as a new reference or already existed. """