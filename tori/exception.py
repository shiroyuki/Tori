# Dependency-injectable Application
class DuplicatedRouteError(Exception):
    '''
    Exception used when the routing pattern is already registered.
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
