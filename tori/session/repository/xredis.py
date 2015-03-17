__MODULE_ENABLED = True

try:
    import cPickle as pickle
except:
    import pickle

try:
    import redis
except ImportError as exception:
    __MODULE_ENABLED = False

from time import time

from tori.exception               import *
from tori.session.repository.base import Base

class Redis(Base):
    def __init__(self, prefix='tori/session', redis_client=None, use_localhost_as_fallback=True):
        if not __MODULE_ENABLED:
            raise ImportError('Failed to enable Redis session storage.')

        Base.__init__(self)

        self._redis = redis_client
        self._prefix = prefix

        self._use_localhost_as_fallback = use_localhost_as_fallback

    @property
    def __api(self):
        if not self._redis and not self._use_localhost_as_fallback:
            raise InvalidInput('The Redis API (PIP: redis) must be provided.')
        elif not self._redis and self._use_localhost_as_fallback:
            pool        = redis.ConnectionPool(host='localhost', port=6379, db=0)
            self._redis = redis.Redis(connection_pool=pool)

        return self._redis

    def __compose_key(self, id, key):
        return '/'.join([self._prefix, id, key])

    def delete(self, id, key):
        actual_key = self.__compose_key(id, key)

        self.__api.delete(actual_key)

    def get(self, id, key):
        actual_key = self.__compose_key(id, key)
        content    = self.__api.get(actual_key)

        if content:
            content = pickle.loads(content)

        return content

    def registered(self, id):
        actual_key = self.__compose_key(id, '*')

        return self.__api.keys(actual_key)

    def reset(self, id):
        self.delete(id, '*')

    def set(self, id, key, content):
        actual_key = self.__compose_key(id, key)

        self.__api.set(actual_key, pickle.dumps(content))