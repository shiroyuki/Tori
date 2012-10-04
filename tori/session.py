# -*- coding: utf-8 -*-

'''
:Author: Juti Noppornpitak

Common module manages sessions with the session ID, key and value.

.. warning:: This module is not tested.
'''

from time import time

from sqlalchemy       import Column
from sqlalchemy.types import Integer, PickleType, String

from .centre     import settings as AppSettings
from .common     import Enigma
from .exception  import *
from .db.entity  import Entity
from .db.service import RelationalDatabaseService as db

class SessionEntity(object):
    '''
    Session Entity is made to be compatible with any
    SQLAlchemy-based database session controller.
    '''

    __tablename__ = 'tori_session'

    id         = Column(Integer, primary_key=True)
    session_id = Column(String(128), index=True)
    key        = Column(String(128), index=True)
    content    = Column(PickleType)

    def __init__(self, session_id, key, content):
        self.session_id = session_id
        self.key        = key
        self.content    = content

class AbstractSession(object):
    ''' Abstract Session Controller '''

    def delete(self, id, key):
        '''
        Delete a session key.

        :param `id`:  session ID
        :param `key`: session data key

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

    def generate(self):
        '''
        Generate the session ID

        :return: Session ID as a string
        '''
        if 'cookie_secret' not in AppSettings:
            raise SessionError, 'This session component could not not be initialized.'

        session_id = None

        while not session_id or self.registered(session_id):
            session_id = Enigma.instance().hash(
                '%s/%s' % (AppSettings['cookie_secret'], time())
            )

        return session_id

    def get(self, id, key, auto_close=True):
        '''
        Set the given content to a session key.

        :param `id`:  session ID
        :param `key`: session data key
        :return:      session data content

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

    def has(self, id, key):
        '''
        Set the given content to a session key.

        :param `id`:  session ID
        :param `key`: session data key
        :return:      ``True`` if there exists the data.
        '''
        return self.get(session_id, key) is not None

    def registered(self, id):
        '''
        Set the given content to a session key.

        :param `id`: session ID
        :return:     ``True`` if the session ID is registered.

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature

    def set(self, id, key, content):
        '''
        Set the given content to a session key.

        :param `id`:      session ID
        :param `key`:     session data key
        :param `content`: session data content
        :return:          session data content

        .. note:: This method is not implemented in :class:`AbstractSession`.
        '''
        raise FutureFeature
    
class MemorySession(AbstractSession):
    ''' In-memory Session Controller '''

    def __init__(self):
        self._storage = {}

    def delete(self, id, key):
        if not self.has(id, key):
            return
        
        del self._storage[id][key]

    def get(self, id, key, auto_close=True):
        if not self.has(id, key):
            return None
        
        raise FutureFeature

    def has(self, id, key):
        return id in self._storage and key in self._storage[id]

    def registered(self, id):
        return id in self._storage

    def set(self, id, key, content):
        if not self.registered(id):
            self._storage[id] = {}
        
        self._storage[id][key] = content

class DbSession(AbstractSession):
    '''
    Session Controller using SQLAlchemy's ORM

    :param `url`: SQLAlchemy-compatible connection URL

    .. note::

        This is based on :class:`AbstractSession`. All non-implementing methods
        in the parent class are implemented. This is only compatible with
        :class:`DbSessionEntity`.

    '''

    def __init__(self, url='sqlite:///:memory:'):
        Console.log('tori.session.DbSession: %s' % url)

        self.db = db(url)

    def base_filter(self, id):
        return self.db.\
            query(DbSessionEntity).\
            filter(DbSessionEntity.session_id==id)

    def commit(self):
        if not self.db.session:
            return

        self.db_session.commit()

    def delete(self, id, key):
        data = self.base_filter(id).\
            filter(DbSessionEntity.key==key).\
            first()

        if not data:
            return

        self.session.delete(data)
        self.commit()

    def get(self, id, key):
        data = self.base_filter(id).\
            filter(DbSessionEntity.key==key).\
            first()

        return data and data.content or None

    def registered(self, id):
        data = self.base_filter(id).all()

        return len(data) > 0

    def set(self, id, key, content):
        data = self.base_filter(id).\
            filter(DbSessionEntity.key==key).\
            first()

        if not data:
            data = DbSessionEntity(id, key, content)
            self.session.add(data)

        data.content = content

        self.commit()
