"""
:Author: Juti Noppornpitak
:Status: Testing
"""

from tori.session.entity.document import Document
from tori.session.repository.base import Base

class Collection(Base):
    """
    Session Controller using MongoDB

    :param `collection`: :class:`passerine.db.repository.Repository`

    .. note::

        This is based on :class:`tori.session.repository.base.Base`. All
        non-implementing methods in the parent class are implemented. This is
        only compatible with :class:`tori.session.entity.document.Document`.

    """

    def __init__(self, collection):
        Base.__init__(self)

        self.collection = collection

    def __get(self, id, key):
        return self.collection.filter_one(session_id=id, key=key)

    def delete(self, id, key):
        self.collection.delete_by_criteria(session_id=id, key=key)

    def get(self, id, key):
        data = self.__get(session_id=id, key=key)

        return data and data.content or None

    def registered(self, id):
        data = self.collection.filter_one(session_id=id)

        return len(data) > 0

    def reset(self, id):
        self.collection.delete_by_criteria(session_id=id)

    def set(self, id, key, content):
        data = self.__get(id, key)

        if not data:
            data = Document(id, key, content)

            self.collection.post(data)

            return

        data.content = content

        self.collection.put(data)