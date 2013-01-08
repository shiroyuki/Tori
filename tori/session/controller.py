"""
:Author: Juti Noppornpitak

This package contains the session controller used with the web controller and socket handler.
"""

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
        """ Administrated Session ID

        :return: str
        """
        return self._id

    def delete(self, key):
        """ Delete the data
        :param key: data key
        :type  key: str
        """
        self._repository.delete(self._id, key)

    def get(self, key):
        """ Retrieve the data

        :param key: data key
        :type  key: str
        :return: the data stored by the given key
        """
        return self._repository.get(self._id, key)

    def set(self, key, content):
        """ Define the data

        :param key: data key
        :type  key: str
        :param content: data content
        """
        self._repository.set(self._id, key, content)

    def reset(self):
        """ Clear out all data of the administrated session """
        self._repository.reset(self._id)
