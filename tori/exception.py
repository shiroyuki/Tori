# Common / Future exception
class FutureFeatureException(Exception):
    '''
    Exception used when the future feature is used where it is not properly implemented.
    '''

# Common / Object Dictionary
class UnsupportObjectTypeError(Exception):
    '''
    Exception used when the unsupported object type is used in an inappropriate place.
    
    Please note that this is a general exception.
    '''

# Decorator / Common / Singleton Decorator
class SingletonInitializationException(Exception):
    '''
    This exception is used when the target class contain a special
    attribute `_singleton_instance` not a reference to its own class.
    '''

# Dependency-injectable Application
class DuplicatedRouteError(Exception):
    '''
    Exception used when the routing pattern is already registered.
    '''

class InvalidControllerDirectiveError(Exception):
    '''
    Exception used when the controller directive is incomplete due to missing parameter
    '''

class RoutingPatternNotFoundError(Exception):
    '''
    Exception used when the routing pattern is not specified in the configuration file.
    '''

class RoutingTypeNotFoundError(Exception):
    '''
    Exception used when the routing type is not specified in the configuration file.
    '''

class UnknownRoutingTypeError(Exception):
    '''
    Exception used when the routing type is not unknown.
    '''

class InvalidRedirectionDirectiveError(Exception):
    '''
    Exception used when the redirection directive is incomplete because some parameters aren't provided or incompatible.
    '''

# Controllers
class RenderingSourceMissingError(Exception):
    '''
    Exception used when the rendering source is not set.
    '''

# Template Repository and Rendering Service
class UnsupportedRendererError(Exception):
    '''
    Exception thrown when the unsupported renderer is being registered.
    '''

class RendererNotFoundError(Exception):
    '''
    Exception thrown when the unknown template repository is used.
    '''
