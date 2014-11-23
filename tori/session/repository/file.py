import json
import hashlib
import urllib
from tori.session.repository.base import Base

class File(Base):
    """ In-memory Session AbstractRepository """

    def __init__(self, location):
        self._storage  = {}
        self._location = location

        try:
            with open(self._location) as f:
                self._storage.update(json.load(f))
        except IOError:
            pass

    def delete(self, id, key):
        if not self.has(id, key):
            return

        del self._storage[id][key]

        self._update_backup()

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

        self._update_backup()

    def set(self, id, key, content):
        if not self.registered(id):
            self._storage[id] = {}

        self._storage[id][key] = content

        self._update_backup()

    def _update_backup(self):
        with open(self._location, 'w') as f:
            json.dump(self._storage, f)
