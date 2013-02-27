# Common / Unexpected Computation
class UnexpectedComputationError(Exception):
    """ Exception used when the code runs mistakenly unexpectedly. """

# Common / Future exception
class FutureFeatureException(Exception):
    """
    Exception used when the future feature is used where it is not properly implemented.
    """

# Common / Invalid input
class InvalidInput(Exception):
    """
    Exception used when the given input is invalid or incompatible to the requirement.
    """

# Common / Object Dictionary
class UnsupportObjectTypeError(Exception):
    """
    Exception used when the unsupported object type is used in an inappropriate place.

    Please note that this is a general exception.
    """

# Decorator / Common / Singleton Decorator
class SingletonInitializationException(Exception):
    """
    This exception is used when the target class contain a special
    attribute `_singleton_instance` not a reference to its own class.
    """

# Dependency-injectable Application
class InvalidConfigurationError(Exception):
    """
    Exception thrown only when the configuration is invalid.
    """

# XML Configuration
class DuplicatedPortError(Exception):
    """
    Exception thrown only when the port config is duplicated within the
    same configuration file.
    """

# Routes
class DuplicatedRouteError(Exception):
    """
    Exception used when the routing pattern is already registered.
    """

class RoutingPatternNotFoundError(Exception):
    """
    Exception used when the routing pattern is not specified in the configuration file.
    """

class RoutingTypeNotFoundError(Exception):
    """
    Exception used when the routing type is not specified in the configuration file.
    """

class UnknownRoutingTypeError(Exception):
    """
    Exception used when the routing type is not unknown.
    """

# Controller Directive
class InvalidControllerDirectiveError(Exception):
    """
    Exception used when the controller directive is incomplete due to missing parameter
    """

# Redirection Directive
class InvalidRedirectionDirectiveError(Exception):
    """
    Exception used when the redirection directive is incomplete because some parameters aren't provided or incompatible.
    """

# Fixtures
class LoadedFixtureException(Exception):
    """ Exception raised when the fixture is loaded. """

# Session
class SessionError(Exception):
    """ Exception thrown when there is an error with session component. """

# Template AbstractRepository and Rendering Service
class RenderingSourceMissingError(Exception):
    """
    Exception used when the rendering source is not set.
    """

class UnsupportedRendererError(Exception):
    """
    Exception thrown when the unsupported renderer is being registered.
    """

class RendererSetupError(Exception):
    """
    Exception thrown when there exists errors during setting up the template.
    """

class RendererNotFoundError(Exception):
    """
    Exception thrown when the unknown template repository is used.
    """

# Services
class UnknownServiceError(Exception):
    """
    Exception thrown when the requested service is unknown or not found.
    """