"""
:Author: Juti Noppornpitak
:Status: Testing/Unstable
"""

from tori.session.entity.database import Database as Entity
from tori.session.repository.base import Base

class Database(Base):
    """
    Session Controller using SQLAlchemy's ORM

    :param `url`: SQLAlchemy-compatible connection URL

    .. note::

        This is based on :class:`AbstractSession`. All non-implementing methods
        in the parent class are implemented. This is only compatible with
        :class:`DbEntity`.

    """

    def __init__(self, db):
        Base.__init__(self)

        self.db = db

    def base_filter(self, id):
        return self.db.\
            query(Entity).\
            filter(Entity.session_id==id)

    def commit(self):
        self.db.session.commit()

    def delete(self, id, key):
        data = self.base_filter(id).\
            filter(Entity.key==key).\
            first()

        if not data:
            return

        self.session.delete(data)
        self.commit()

    def get(self, id, key):
        data = self.base_filter(id).\
            filter(Entity.key==key).\
            first()

        return data and data.content or None

    def registered(self, id):
        data = self.base_filter(id).all()

        return len(data) > 0

    def reset(self, id):
        data_list = self.base_filter(id).all()

        for data in data_list:
            self.session.delete(data)

        self.commit()

    def set(self, id, key, content):
        data = self.base_filter(id).\
            filter(Entity.key==key).\
            first()

        if not data:
            data = Entity(id, key, content)

            self.session.add(data)
        else:
            data.content = content

        self.commit()