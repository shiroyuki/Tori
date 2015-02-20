from tori.session.entity.base import Base
from passerine.db.entity         import entity

@entity
class Document(Base):
    """
    Entity Session Entity is made to use with a Repository session repository (MongoDB).
    """
    def __init__(self, session_id, key, content, _id=None):
        Base.__init__(self, session_id, key, content)

        self._id = _id
