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
