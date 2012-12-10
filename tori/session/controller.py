from imagination.decorator.validator import restrict_type
from tori.session.repository.base    import Base

class Controller(object):
    """
    A session controller for the controller (request handler).
    """
    @restrict_type(Base)
    def __init__(self, session_repository, id):
        self._repository = session_repository
        self._id         = id

    @property
    def id(self):
        return self._id

    def delete(self, key):
        self._repository.delete(self._id, key)

    def get(self, key):
        return self._repository.get(self._id, key)

    def set(self, key, content):
        self._repository.set(self._id, key, content)

    def reset(self):
        """ Clear out all data of the specified session. """
        self._repository.reset(self._id)
