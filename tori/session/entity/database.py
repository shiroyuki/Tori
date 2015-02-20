# Deprecated
from sqlalchemy       import Column
from sqlalchemy.types import Integer, PickleType, String

from passerine.db.wrapper           import Entity
from tori.session.entity.base import Base

class Database(Base, Entity):
    """
    DB Session Entity is made to use with a DB session repository.
    """

    __tablename__ = 'tori_session'

    id          = Column(Integer, primary_key=True)
    _session_id = Column(String(128), index=True)
    key         = Column(String(128), index=True)
    content     = Column(PickleType)