from tori.exception import *

class Base(object):
    """ The Base AbstractRepository """

    def __init__(self):
        pass

    def delete(self, id, key):
        """
        Delete a session key.

        :param `id`:  session ID
        :param `key`: session data key

        .. note:: This method is not implemented in :class:`tori.session.repository.base.Base`.
        """
        raise FutureFeatureException

    def generate(self):
        """
        Generate the session ID

        :return: Session ID as a string
        """
        if 'cookie_secret' not in AppSettings:
            raise SessionError('This session component could not not be initialized.')

        session_id = None

        while not session_id or self.registered(session_id):
            session_id = self.guidGenerator.generate()

        return session_id

    def get(self, id, key):
        """
        Set the given content to a session key.

        :param `id`:  session ID
        :param `key`: session data key
        :return:      session data content

        .. note:: This method is not implemented in :class:`tori.session.repository.base.Base`.
        """
        raise FutureFeatureException

    def has(self, id, key):
        """
        Set the given content to a session key.

        :param `id`:  session ID
        :param `key`: session data key
        :return:      ``True`` if there exists the data.
        """
        return self.get(session_id, key) is not None

    def registered(self, id):
        """
        Set the given content to a session key.

        :param `id`: session ID
        :return:     ``True`` if the session ID is registered.

        .. note:: This method is not implemented in :class:`tori.session.repository.base.Base`.
        """
        raise FutureFeatureException

    def reset(self, id):
        """
        Remove all data associated to the specified session.

        :param `id`:  session ID

        .. note:: This method is not implemented in :class:`tori.session.repository.base.Base`.
        """
        raise FutureFeatureException

    def set(self, id, key, content):
        """
        Set the given content to a session key.

        :param `id`:      session ID
        :param `key`:     session data key
        :param `content`: session data content
        :return:          session data content

        .. note:: This method is not implemented in :class:`tori.session.repository.base.Base`.
        """
        raise FutureFeatureException
