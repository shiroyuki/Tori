class DuplicatedRelationalMapping(Exception):
    """ Exception thrown when the property is already mapped. """

class UnavailableCollectionException(Exception):
    """ Exception thrown when the collection is not available. """

class LockedIdException(Exception):
    """ Exception thrown when the ID is tempted to change. """

class MissingObjectIdException(Exception):
    """ Exception raised when the object Id is not specified during data retrieval. """

class UOWRepeatedRegistrationError(IOError):
    """ Error thrown when the given reference is already registered as a new reference or already existed. """

class UOWUnknownRecordError(IOError):
    """ Error thrown when the given reference is already registered as a new reference or already existed. """

class UOWUpdateError(IOError):
    """ Error thrown when the given reference is already registered as a new reference or already existed. """

class ReadOnlyProxyException(Exception):
    """ Exception raised when the proxy is for read only. """

class IntegrityConstraintError(RuntimeError):
    """ Runtime Error raised when the given value violates a integrity constraint. """