from tori.session.repository.base import Base

class Memory(Base):
    """ In-memory Session AbstractRepository """

    def __init__(self):
        self._storage = {}

    def delete(self, id, key):
        if not self.has(id, key):
            return

        del self._storage[id][key]

    def get(self, id, key, auto_close=True):
        if not self.has(id, key):
            return None

        return self._storage[id][key]

    def has(self, id, key):
        return id in self._storage and key in self._storage[id]

    def registered(self, id):
        return id in self._storage

    def reset(self, id):
        del self._storage[id]

    def set(self, id, key, content):
        if not self.registered(id):
            self._storage[id] = {}

        self._storage[id][key] = content