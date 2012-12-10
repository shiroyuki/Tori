class Base(object):
    """
    Basic Session Entity is the base entity representing the data in thte session.
    """

    def __init__(self, session_id, key, content):
        self._session_id = session_id
        self.key         = key
        self.content     = content

    @property
    def session_id(self):
        return self._session_id